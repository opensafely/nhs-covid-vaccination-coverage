library(ggplot2)
library(dplyr)
library(here)
library(readr)
library(tidyr)
library(dplyr)
library(data.table)
library(cowplot)
library(RColorBrewer)
library(purrr)
library(stringr)
library(glue)
library(colorspace)

### Find the data files
data_location = here::here("interim-outputs", "u16", "tables")
files_to_read = dir(data_location, pattern = "^Cumulative vaccination figures *", full.names = TRUE)

###  Combine the data files
concatenate_data_files = function(x, columns = c("src", "category", "group", "vaccinated", "total", "percent")) {
    src_string = x %>%
        basename() %>%
        str_replace(".* among ", "") %>%
        str_replace(" population.csv", "")
    tmp = read_csv(x) %>% mutate(src = src_string)
    return(tmp[columns])
}

combined_data = files_to_read %>%
    map(concatenate_data_files) %>%
    rbindlist() %>%
    as.data.frame()

### Write out the table
output_table = combined_data %>%
    tidyr::pivot_wider(
        names_from = "src",
        values_from = c("vaccinated", "total", "percent"),
        id_cols = c("category", "group")
    ) %>%
    mutate(category = category %>%
        str_replace("_6_groups", " (broad categories)") %>%
        str_replace("_16_groups", " (detailed categories)") %>%
        str_replace_all("_", " ") %>%
        str_to_sentence() %>%
        str_replace("Imd categories", "IMD")) 

output_table = output_table[c(
    "category", "group",
    "vaccinated_12-15", "total_12-15", "percent_12-15",
    "vaccinated_5-11", "total_5-11", "percent_5-11"
)]

new_column_names = output_table %>%
    colnames() %>%
    str_replace("_(\\d+-\\d+)", " \\(\\1\\)") %>%
    str_replace("vaccinated", "Vaccinated (n)") %>%
    str_replace("total", "Total eligible (n)") %>%
    str_replace("percent", "Vaccinated (%)") %>%
    str_replace( "category", "Category" ) %>%
    str_replace( "group", "Group" )

new_column_names = new_column_names[
    c(
        new_column_names %>% str_detect("Category") %>% which(),
        new_column_names %>% str_detect("Group") %>% which(),
        new_column_names %>% str_detect("12-15") %>% which(),
        new_column_names %>% str_detect("5-11") %>% which()
    )
]

colnames(output_table) = new_column_names

output_table %>% write_csv(here::here("interim-outputs", "u16", "tables", "u16_publication_table.csv"))

### Draw a figure

fig_data = combined_data %>%
    filter(category != "Brand of first dose") %>%
    select(src, category, group, percent) %>%
    rename(Cohort = src) %>%
    mutate(percent_rounded = sprintf("%.1f", percent))


palette_name = "Paired"

fill_colours = list(
    "12-15" = brewer.pal(9,"YlOrRd")[5] %>% lighten,
    "5-11" = brewer.pal(9, "YlGnBu")[5] %>% lighten
    # "12-15" = brewer.pal(3,"Paired")[2] %>% lighten,
    # "5-11"  = brewer.pal(3,"Paired")[1] %>% lighten
)



# ### COHORTS side by side

demographic_plots <- lapply(split(fig_data, fig_data$category), function(x) {
    ggplot(x, aes(x = group, y = percent, fill = Cohort)) +
        geom_col(position = "dodge") +
        ylim(0, 100) +
        scale_fill_manual(values=fill_colours) +
        theme_minimal() +
        theme( axis.text.x = element_text(size=8) )+
        ylab(NULL) +
        xlab(NULL)
})

legend <- get_legend(
    # create some space to the left of the legend
    demographic_plots$overall +
        guides(color = guide_legend(nrow = 1)) +
        theme(legend.position = "bottom")
)

### COHORTS combined

max_y = combined_data %>% pull(percent) %>% max %>% round( digits = -1 )


fig_data_focus = fig_data %>% filter( category != "overall" )
overall_values = fig_data %>% filter( category == "overall" )


fig_data_focus = fig_data_focus %>%
    mutate(group = group %>%
        str_replace( "F$", "F\n ") %>%
        str_replace( "M$", "M\n ") %>%
        str_replace("risk group", "\n risk group") %>%
        str_replace("South Asian", "South\n Asian" ) %>%
        str_replace("Most deprived", "\nMost deprived") %>%
        str_replace("Least deprived", "\nLeast deprived"))



### Version 1: without percentage labels

overall_colour <- grey.colors(7)[3]
these_plot_margins <- unit(c(25, 5, 5, 5), "points")
top_plot_margins = unit(c(25, 5, 2, 5), "points")


demographic_plots_combined <- lapply(split(fig_data_focus, fig_data_focus$category), function(x) {
    this_plot = ggplot(x, aes(x = group, y = percent, fill = Cohort)) +
        # "Overall" annotation - line
        geom_hline(data = overall_values, aes(yintercept = percent), colour = overall_colour, linetype = "dashed") +
        # Data
        geom_col() +
        facet_wrap(~Cohort, scales = "free_y") +
        scale_fill_manual(values = fill_colours) +
        # "Overall" annotation - label
        geom_text(data = overall_values, aes(x = 0, y = percent, label = percent_rounded), size = 3, hjust = 0, vjust = -0.5, colour = overall_colour) +
        # Theme/visuals
        theme_minimal() +
        theme(
            axis.text.x = element_text(size = 8),
            axis.title.y = element_text(face="bold"),
            panel.grid.major.x = element_blank(),
            panel.grid.minor.x = element_blank(),
            strip.text = element_blank(),
            plot.margin = these_plot_margins
        ) +
        ylab("Percent") +
        xlab(NULL) +
        ### Stop text labels falling off the top
        coord_cartesian(clip = "off")
 
})

demographic_plots_combined_annotated = demographic_plots_combined


top_row_combined_annotated <- plot_grid(
    demographic_plots_combined_annotated$sex + theme(legend.position = "none",
            plot.margin = top_plot_margins),
    demographic_plots_combined_annotated$risk_status + theme(legend.position = "none",
            plot.margin = top_plot_margins),
    ncol = 2,
    rel_widths = c(1, 1),
    labels = c("Sex", "Risk status"),
    label_size = 14,
    label_x = 0.05
)

demographics_matrix_combined_annotated <- plot_grid(top_row_combined_annotated,
    demographic_plots_combined_annotated$imd_categories + theme(legend.position = "none"),
    demographic_plots_combined_annotated$ethnicity_6_groups + theme(legend.position = "none"),
    demographic_plots_combined_annotated$ethnicity_16_groups + theme(legend.position = "none", axis.text.x = element_text(angle = 90, hjust = 1)),
    legend,
    rel_heights = c(2, 2, 2, 4, 0.2),
    ncol = 1,
    labels = c("", "Index of multiple deprivation", "Ethnicity (broad categories)", "Ethnicity (detailed categories)", ""),
    label_size = 14,
    label_x = 0.05,
    hjust = 0
)

save_plot(here::here("interim-outputs", "u16", "figures", "u16_publication_figure.png"),
# save_plot("tmp.png",
    demographics_matrix_combined_annotated,
    base_width = 9, base_height = 10
)



### Version 2: Add percentage labels

fig_data_focus = fig_data_focus %>%
    mutate(percent_rounded = sprintf("%.1f", percent))


demographic_plots_combined <- lapply(split(fig_data_focus, fig_data_focus$category), function(x) {
    this_plot <- ggplot(x, aes(x = group, y = percent, fill = Cohort)) +
        # "Overall" annotation - line
        geom_hline(data = overall_values, aes(yintercept = percent), colour = overall_colour, linetype = "dashed") +
        # Data
        geom_col() +
        facet_wrap(~Cohort, scales = "free_y") +
        scale_fill_manual(values = fill_colours) +
        # "Overall" annotation - label
        geom_text(data = overall_values, aes(x = 0, y = percent, label = percent_rounded), size = 3, hjust = 0, vjust = -0.5, colour = overall_colour) +
        geom_text( aes(label=percent_rounded), y=0, angle=90, size=3, hjust=-0.4 ) +
        # Theme/visuals
        theme_minimal() +
        theme(
            axis.text.x = element_text(size = 8),
            axis.title.y = element_text(face = "bold"),
            panel.grid.major.x = element_blank(),
            panel.grid.minor.x = element_blank(),
            strip.text = element_blank(),
            plot.margin = these_plot_margins
        ) +
        ylab("Percent") +
        xlab(NULL) +
        ### Stop text labels falling off the top
        coord_cartesian(clip = "off")
})

demographic_plots_combined_annotated = demographic_plots_combined


top_row_combined_annotated <- plot_grid(
    demographic_plots_combined_annotated$sex + theme(
        legend.position = "none",
        plot.margin = top_plot_margins
    ),
    demographic_plots_combined_annotated$risk_status + theme(
        legend.position = "none",
        plot.margin = top_plot_margins
    ),
    ncol = 2,
    rel_widths = c(1, 1),
    labels = c("Sex", "Risk status"),
    label_size = 14,
    label_x = 0.05
)

demographics_matrix_combined_annotated <- plot_grid(top_row_combined_annotated,
    demographic_plots_combined_annotated$imd_categories + theme(legend.position = "none"),
    demographic_plots_combined_annotated$ethnicity_6_groups + theme(legend.position = "none"),
    demographic_plots_combined_annotated$ethnicity_16_groups + theme(legend.position = "none", axis.text.x = element_text(angle = 90, hjust = 1)),
    legend,
    rel_heights = c(2, 2, 2, 4, 0.2),
    ncol = 1,
    labels = c("", "Index of multiple deprivation", "Ethnicity (broad categories)", "Ethnicity (detailed categories)", ""),
    label_size = 14,
    label_x = 0.05,
    hjust = 0
)

save_plot(here::here("interim-outputs", "u16", "figures", "u16_publication_figure_labels.png"),
    # save_plot("tmp.png",
    demographics_matrix_combined_annotated,
    base_width = 9, base_height = 10
)
