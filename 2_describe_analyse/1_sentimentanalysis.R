library(tidyverse)
library(data.table)
library(ggpubr)
library(scales)
library(stringr)

options(scipen=999)

df_all <- fread("converted/dataset_complete_sentiment2.csv")

# Filter out works before 1913
df <- df_all %>%
  filter(pubyear_cleaned >= 1913)

# Create relevant data
df <- df %>%
  mutate(cohort = cut(birth_year_final, breaks = seq(1800, 2000, by = 10)),
         period = pubyear_cleaned)


###
# Description
###
length(unique(df$final_gnd_id))

length(unique(df$age))
summary(df$age)
sd(df$age)

length(unique(df$birth_year_final))
summary(df$birth_year_final)
summary(df$cohort)

length(unique(df$pubyear_cleaned))
summary(df$pubyear_cleaned)

table(df$belletristik)
table(df$no_ddc)


#books across time
book_counts <- as.data.frame(table(df$pubyear_cleaned))

df_counts <- df %>%
  group_by(pubyear_cleaned) %>%
  summarize(Count = n()) %>%
  ungroup() 

ggplot(df_counts, aes(x = pubyear_cleaned, y = Count, fill = belletristik)) +
  geom_bar(stat = "identity", fill = "lightblue", color = "black") +
  scale_x_continuous(breaks = seq(1910, 2050, by = 20)) +
  xlab("Year of Publication") +
  ylab("Book Count") +
  labs(fill = "") +
  ggtitle("Books Published per Year") +
  theme_minimal(base_size = 20) +
  theme(legend.position="bottom")

ggsave("5_Results/figures/plotbooksperyear.pdf", 
       last_plot(), 
       units = "cm",
       width = 30,
       height = 20)


#per birthyear
df_counts <- df %>%
  group_by(birth_year_final) %>%
  summarize(Count = n()) %>%
  ungroup() 

ggplot(df_counts, aes(x = birth_year_final, y = Count, fill = belletristik)) +
  geom_bar(stat = "identity", fill = "lightblue", color = "black") +
  xlab("Birth Year of Author") +
  ylab("Book Count") +
  labs(fill = "") +
  ggtitle("Books Published per Birth Year") +
  theme_minimal(base_size = 20) +
  theme(legend.position="bottom")

ggsave("5_Results/figures/plotbookspercohort.pdf", 
       last_plot(), 
       units = "cm",
       width = 30,
       height = 20)

#per age
df_counts <- df %>%
  group_by(age) %>%
  summarize(Count = n()) %>%
  ungroup() 

# Create stacked bar plot
ggplot(df_counts, aes(x = age, y = Count, fill = belletristik)) +
  geom_bar(stat = "identity", fill = "lightblue", color = "black") +
  xlab("Birth Year of Author") +
  ylab("Book Count") +
  labs(fill = "") +
  ggtitle("Books Published per Birth Year") +
  theme_minimal(base_size = 20) +
  theme(legend.position="bottom")

ggsave("5_Results/figures/plotbooksperage.pdf", 
       last_plot(), 
       units = "cm",
       width = 30,
       height = 20)


average_age_per_year <- df %>%
  group_by(pubyear_cleaned) %>%
  summarise(average_age = quantile(age, 0.25, na.rm = TRUE)) %>%
  ungroup

average_age_per_year <- df %>%
  group_by(pubyear_cleaned) %>%
  summarise(average_age = mean(age, na.rm = TRUE)) %>%
  ungroup


ggplot(average_age_per_year, aes(x = pubyear_cleaned, y = average_age)) +
  geom_line(color = "darkblue") +
  #geom_point() +
  scale_x_continuous(limits = c(1910, max(df$pubyear_cleaned)),
                     breaks = seq(1910, max(df$pubyear_cleaned), by = 20)) +
  labs(x = "Publication Year", y = "Average Age") +
  ggtitle("Average Age per Publication Year") +
  theme_minimal(base_size = 20) 
  
ggsave("5_Results/figures/plotageperbook.pdf", 
       last_plot(), 
       units = "cm",
       width = 30,
       height = 20)


#Describe title
df$NumWords <- str_count(df$title_subtitle, "\\S+")


summary(df$NumWords, na.rm=FALSE)
sd(df$NumWords)

single_word_titles <- df$title_subtitle[df$NumWords == 1]
head(single_word_titles)
long_word_titles <- df$title_subtitle[df$NumWords == 285]
head(long_word_titles)

top_10_titles <- df$title_subtitle[order(-df$NumWords)][1:80]
# Print the top 10 titles
print(top_10_titles)


plottitleslim <- ggplot(df, aes(x = NumWords)) +
  geom_histogram(binwidth = 1, fill = "lightblue", color = "black") +
  #scale_fill_manual(values = c("TRUE" = "darkblue", "FALSE" = "lightblue"),
  #                  labels = c("TRUE" = "Belletristik", "FALSE" = "Sachliteratur")) +
  labs(title = "Distribution of Number of Words in the Titles",
       x = "Number of Words", y = "Frequency") +
  labs(fill = "") +
  xlim(0, 30) + #eins mit lim, eins ohne
  theme_minimal(base_size = 20)
  
plottitles <- ggplot(df, aes(x = NumWords)) +
  geom_histogram(binwidth = 1, fill = "lightblue", color = "black") +
  #scale_fill_manual(values = c("TRUE" = "darkblue", "FALSE" = "lightblue"),
  #                  labels = c("TRUE" = "Belletristik", "FALSE" = "Sachliteratur")) +
  labs(#title = "Distribution of number of words in the titles",
       x = "Number of Words", y = "") +
  labs(fill = "") +
  theme_minimal(base_size = 20)
  
plottitlesarrange <- ggarrange(plottitleslim, plottitles, nrow = 1, ncol = 2, common.legend = TRUE, legend = "bottom")
plottitlesarrange

ggsave("5_Results/figures/plottitlesarrange.pdf", 
       plottitlesarrange, 
       units = "cm",
       width = 30,
       height = 20)


#keywords description
df$keywords_cleaned_2 <- str_replace_all(df$keywords_cleaned, "nan", "")
df$keywords_cleaned2_2 <- str_replace_all(df$keywords_cleaned2, "nan", "")
df$keywords_cleaned2_2 <- ifelse(is.na(df$keywords_cleaned2_2), "", df$keywords_cleaned2_2)

df$keywordscombined <-  paste(df$keywords_cleaned_2, df$keywords_cleaned2_2, sep=" ")
head(df$keywords_cleaned2_2)

df$NumWords_keywords <- str_count(df$keywordscombined, "\\S+")

head(df$keywords_cleaned_2)

summary(df$NumWords_keywords, na.rm=FALSE)
sd(df$NumWords_keywords)

avg_word_count_keywords <- aggregate(NumWords_keywords ~ pubyear_cleaned, data = df, FUN = mean)

ggplot(avg_word_count_keywords, aes(x = pubyear_cleaned, y = NumWords_keywords)) +
  geom_line(color = "darkblue", linewidth=1.3) +
  geom_point(color = "darkblue", size=2) +
  scale_x_continuous(limits = c(1910, max(df2$pubyear_cleaned)),
                     breaks = seq(1910, max(df2$pubyear_cleaned), by = 20)) +
  scale_y_continuous(limits = c(0, max(avg_word_count_keywords$NumWords_keywords))) +
  labs(x = "Publication Year", y = "Average Number of Key Words") +
  ggtitle("Average Number of Keywords by Publication Year") +
  theme_minimal(base_size = 20)

ggsave("5_Results/figures/plotlengthofkeywords.pdf",
       last_plot(),
       units = "cm",
       width = 30,
       height = 20)



avg_word_count <- aggregate(NumWords ~ pubyear_cleaned, data = df, FUN = mean)

ggplot(avg_word_count, aes(x = pubyear_cleaned, y = NumWords)) +
  geom_line(linewidth=0.8, color = "darkblue") +
  scale_x_continuous(limits = c(1910, max(df$pubyear_cleaned)),
                     breaks = seq(1910, max(df$pubyear_cleaned), by = 20)) +
  labs(x = "Publication Year", y = "Average Length of Book Title", color = "") +
  ggtitle("Average Title Length by Publication Year") +
  theme_minimal(base_size = 20) +
  theme(legend.position="bottom")

ggsave("5_Results/figures/plotlengthoftitle.pdf", 
       last_plot(), 
       units = "cm",
       width = 30,
       height = 20)


#content of titles
library(tidytext)
library(tm)

df_tokens <- df %>%
  unnest_tokens(word, title_subtitle)

word_freq <- df_tokens %>%
  count(word, sort = TRUE)

german_stopwords <- stopwords("de")

word_freq <- anti_join(word_freq, data.frame(word = german_stopwords), by = "word")

custom_stop_words <- c("über", "für", "für","über","and", "the")
word_freq <- word_freq[!word_freq$word %in% custom_stop_words, ]

word_freq <- word_freq %>%
  filter(nchar(word) >= 3)

word_freq <- word_freq[order(-word_freq$n), ]


top_n_words <- 15
#top_words <- word_freq[1:top_n_words, ]

# Group the word frequency by the "belletristik" column and display top words for each category
top_words <- word_freq %>%
  slice_max(n, n = top_n_words)

top_words


# Describe sentiment
df %>%
  select(title_sentiment, title_sentiment_AI) %>%
  summary()

sd(df$title_sentiment)
sd(df$title_sentiment_AI)

cor.test(df$title_sentiment, df$title_sentiment_AI)


#Describe title
# Show top/bottom 15 rows with highest title_sentiment
top_15 <- df %>%
  arrange(desc(title_sentiment)) %>%
  select(title_subtitle, title_sentiment, title_sentiment_AI) %>%
  head(15)

bottom_15 <- df %>%
  arrange(title_sentiment) %>%
  select(title_subtitle, title_sentiment, title_sentiment_AI) %>%
  head(15)

combined_rows <- rbind(top_15, bottom_15)
View(combined_rows)

top_15 <- df %>%
  arrange(desc(title_sentiment_AI)) %>%
  select(title_subtitle, title_sentiment, title_sentiment_AI) %>%
  head(15)

bottom_15 <- df %>%
  arrange(title_sentiment_AI) %>%
  select(title_subtitle, title_sentiment, title_sentiment_AI) %>%
  head(15)

combined_rows <- rbind(top_15, bottom_15)
View(combined_rows)



#models
library(mgcv)
library(APCtools)
library(ggpubr)

options(repr.plot.width = 12, repr.plot.height = 6)

# create histograms and line plots for age, pubyear, and cohort
age_hist <- ggplot(df, aes(x = age)) +
  geom_histogram(binwidth = 3, fill = "darkblue") +
  labs(x = "Age", y = "# of books") +
  theme_pubclean(base_size=20)

age_line <- df %>% 
  group_by(age) %>% 
  summarise(avg_sentiment = mean(title_sentiment)) %>% 
  ggplot(aes(x = age, y = avg_sentiment)) +
  geom_line(color = "darkblue") +
  labs(x = "Age", y = "Average sentiment") +
  ylim(-1, 1) +
  theme_minimal(base_size=20)

year_hist <- ggplot(df, aes(x = pubyear_cleaned)) +
  geom_histogram(binwidth = 1, fill = "darkblue") +
  labs(x = "Publication year", y = "") +
  theme_pubclean(base_size=20)

year_line <- df %>% 
  group_by(pubyear_cleaned) %>% 
  summarise(avg_sentiment = mean(title_sentiment)) %>% 
  ggplot(aes(x = pubyear_cleaned, y = avg_sentiment)) +
  geom_line(color = "darkblue") +
  labs(x = "Publication year", y = "") +
  ylim(-1, 1) +
  theme_minimal(base_size=20)

cohort_hist <- ggplot(df, aes(x = birth_year_final)) +
  geom_histogram(binwidth = 5, fill = "darkblue") +
  labs(x = "Cohort (birth year)", y = "") +
  theme_pubclean(base_size=20)

cohort_line <- df %>% 
  group_by(birth_year_final) %>% 
  summarise(avg_sentiment = mean(title_sentiment)) %>% 
  ggplot(aes(x = birth_year_final, y = avg_sentiment)) +
  geom_line(color = "darkblue") +
  labs(x = "Cohort (birth year)", y = "") +
  ylim(-1, 1) +
  theme_minimal(base_size=20)


# arrange plots 
ggarrange(age_hist, year_hist, cohort_hist,
          age_line, year_line, cohort_line, 
          ncol = 3, nrow = 2, heights = c(1, 5), 
          common.legend = TRUE, legend = "bottom") 


ggsave("5_Results/figures/plotsentimentsanalysis.pdf", 
       last_plot(), 
       units = "cm",
       width = 35,
       height = 40)


#zoomed in
age_linez <- df %>% 
  group_by(age) %>% 
  summarise(avg_sentiment = mean(title_sentiment)) %>% 
  ggplot(aes(x = age, y = avg_sentiment)) +
  geom_line(color = "darkblue") +
  labs(x = "Age", y = "Average sentiment") +
  theme_minimal(base_size=20)

year_linez <- df %>% 
  group_by(pubyear_cleaned) %>% 
  summarise(avg_sentiment = mean(title_sentiment)) %>% 
  ggplot(aes(x = pubyear_cleaned, y = avg_sentiment)) +
  geom_line(color = "darkblue") +
  labs(x = "Publication year", y = "") +
  theme_minimal(base_size=20)

cohort_linez <- df %>% 
  group_by(birth_year_final) %>% 
  summarise(avg_sentiment = mean(title_sentiment)) %>% 
  ggplot(aes(x = birth_year_final, y = avg_sentiment)) +
  geom_line(color = "darkblue") +
  labs(x = "Cohort (birth year)", y = "") +
  theme_minimal(base_size=20)

ggarrange(age_linez, year_linez, cohort_linez, 
          ncol = 3, nrow = 1, heights = c(1, 5), 
          common.legend = TRUE, legend = "bottom") 


ggsave("5_Results/figures/plotsentimentsanalysiszoom.pdf", 
       last_plot(), 
       units = "cm",
       width = 35,
       height = 30)



year_line <- df %>% 
  group_by(pubyear_cleaned) %>% 
  summarise(avg_sentiment = mean(title_sentiment)) %>% 
  ggplot(aes(x = pubyear_cleaned, y = avg_sentiment)) +
  geom_line(color = "darkblue") +
  labs(x = "Publication year", y = "") +
  coord_cartesian(ylim = c(0.01, 0.08)) +
  scale_x_continuous(breaks = seq(1910, 2020, 10)) +
  theme_pubclean(base_size=20)
year_line  




plot_APCheatmap(df, "title_sentiment", bin_heatmap = FALSE)

plot_APChexamap(df, "title_sentiment")

plot_APCheatmap(dat            = df,
                y_var          = "title_sentiment",
                bin_heatmap    = FALSE,
                markLines_list = list(cohort = c(1900,1920,1940,
                                                 1960,1980))) +
  scale_color_continuous(guide = color_guide)

ggsave("5_Results/figures/plotsentimentheatmap.pdf", 
       last_plot(), 
       units = "cm",
       width = 35,
       height = 30)

plot_APChexamap(dat            = df,
                y_var          = "title_sentiment")

ggsave("5_Results/figures/plotsentimenthexamap.pdf", 
       last_plot(), 
       units = "cm",
       width = 35,
       height = 30)


#Model
model_pure <- gam(title_sentiment ~ te(age, period,  bs = "ps", k = c(5,5)),
                  data = df)

summary(model_pure)

model_list <- list(model_pure)

summary_list <- create_modelSummary(model_list)
summary_list[[1]]
summary_list[[2]]


#model_panel <- gam(title_sentiment ~ te(age, period, bs = "ps", k = c(5, 5)) + factor(final_gnd_id), data = df)
#df$final_gnd_id_fac <- factor(df$final_gnd_id)
#model_panel <- gam(title_sentiment ~ te(age, period, bs = "ps", k = c(5, 5)) + s(final_gnd_id_fac, bs = "re"), data = df)


plot_APCheatmap(dat = df, model = model_pure)
plot_APChexamap(dat = df, model = model_pure)

ggsave("5_Results/figures/modelresultshexamap.pdf", 
       last_plot(), 
       units = "cm",
       width = 35,
       height = 30)


marginalage <- plot_marginalAPCeffects(model = model_pure,
                        dat = df,
                        variable = "age")  +
  geom_line(color = "darkblue") + theme_pubclean(base_size=18)


marginalperiod <- plot_marginalAPCeffects(model = model_pure,
                        dat = df,
                        variable = "period") +
  geom_line(color = "darkblue") + theme_pubclean(base_size=18)


marginalcohort <- plot_marginalAPCeffects(model = model_pure,
                        dat = df,
                        variable = "cohort") +
  geom_line(color = "darkblue") + theme_pubclean(base_size=18)


ggarrange(marginalage, marginalperiod, marginalcohort,
          ncol = 3, nrow = 1, heights = c(1, 5)) 


ggsave("5_Results/figures/modelresultsmarginal.pdf", 
       last_plot(), 
       units = "cm",
       width = 35,
       height = 30)

create_APCsummary(model_list = model_pure, dat = df)