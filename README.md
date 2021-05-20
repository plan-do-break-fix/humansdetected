# Humans Detected

A website to bring attention to the documents that bring attention to the humans that make websites

---

## Motivation

In 2001, Carlos Mańas, Maria Macias, Abel Cabans, Abel Sutilo and Juanjo Bernabeu started an initiative to bring more attention to the humans behind websites. If websites have a robots.txt, why not a humans.txt? I'm interested in finding out how far humans.txt has spread in the ten years since it began. How widely the humans.txt has been implemented? How many of the humans.txt files on the Internet are structured using [the standard] first used by [Abel Cabans]? How many are in a language other than English and how many multilingual humans.txts are out there? How many have ASCII art? The shortest humans.txt is undoubtedly an empty file, but what is in the longest humans.txt? There are a lot of interesting although not necessarily vital questions that could be asked. To begin to provides some answers, Humans Detected will check the million most-referred domains for a humans.txt file and analyze the contents of any that it finds.

## The Survey

A million thanks to Majestic for the [The Majestic Million], a free list of the top million domains. A comparable list from Alexa Top Sites would cost [$2500] USD. After thorough financial analysis, "free" was determined to be a better fit with the project's budget.

A million domains sounds like a large amount and while it is, it's also not. According to [Verisign], there were over 366 million registered domains at the beginning of 2021, and that number has done nothing but continue to grow. Considering that subdomains can additionally have their own humans.txt independent of any the TLD might have, one million domains is a big number but a tiny percentage. Regardless, it is a start. There is currently no plan for where to find that next million domains to survey, but there is boundless faith that something will work out.

The survey application consists of a MySQL Docker container and a fleet of Agent containers that make GET requests for `domain.tld/humans.txt` and record the result. 

## The Website

Coming soonish.

[$2500]: https://aws.amazon.com/marketplace/pp/B07QK2XWNV?ref_=srh_res_product_title
[Abel Cabans]: https://humanstxt.org/humans.txt
[The Majestic Million]: https://majestic.com/reports/majestic-million
[the standard]: https://humanstxt.org/Standard.html
[Verisign]: https://www.verisign.com/en_US/domain-names/dnib/index.xhtml
