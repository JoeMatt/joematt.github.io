## Extensions

### hugo-loremipsum

<!-- [![Awesome](https://awesome.re/badge.svg)](https://github.com/budparr/awesome-hugo) -->

#### About

This is not a standalone theme. It is a [Hugo](https://gohugo.io) theme component providing a shortcode: `loremipsum` to generate greek text paragraphs.

It starts off with a standard "Lorem ipsum …" text, then randomises the sentence order on each subsequent paragraph.

#### Usage

1. Add the `hugo-loremipsum` as a submodule to be able to get upstream changes later `git submodule add https://github.com/martignoni/hugo-loremipsum.git themes/hugo-loremipsum`
2. Add `hugo-loremipsum` as the left-most element of the `theme` list variable in your site's or theme's configuration file `config.yaml` or `config.toml`. Example, with `config.yaml`:
    ```yaml
    theme: ["hugo-loremipsum", "my-theme"]
    ```
    or, with `config.toml`,
    ```toml
    theme = ["hugo-loremipsum", "my-theme"]
    ```
3. In your site, use the shortcode, e.g. to generate 3 paragraphs of Lorem ipsum greek text :
    ```go
    {{< loremipsum 3 >}}
    ```
    or simply, for just one paragraph
    ```go
    {{< loremipsum >}}
    ```

### hugo-social-metadata

#### About

This is a [Hugo](https://gohugo.io) theme component that automatically generates metadata complying to [The Open Graph Protocol](https://ogp.me/) as well as [Twitter Cards](https://developer.twitter.com/en/docs/tweets/optimize-with-cards/guides/getting-started). This is **NOT** a standalone theme and must not be treated as such.

#### Usage

1. Add the hugo-social-metadata repository as a submodule to be able to get upstream changes later `git submodule add https://github.com/msfjarvis/hugo-social-metadata.git themes/hugo-social-metadata`

2. Start off by configuring a few things in your `config.toml` (or equivalent file depending on whether you use YAML or JSON). These will be picked up by the theme component and used to provide metadata for the site.

```toml
[params]
  description = "A description for your awesome website goes here"
  keywords = "some, keywords, that, describe, your, content"
  twitterUsername = "@your_twitter_username"
  socialImage = "path/to/the/twitter/card/image"
```

3. Include the `hugo-social-metadata` theme as the leftmost element of the theme list variable in your config file. For `config.toml`, it will look something like this:

```toml
theme = ["hugo-social-metadata", "hyde"]
```

4. Include the `social_metadata.html` partial in your `head.html` like so: `{{ partial "social_metadata.html" . }}`.

#### Additional customizations

You can customize some of the generated metadata on a per-page basis. Setting `description`, `socialImage` or `tags` in the frontmatter will override the defaults loaded from the main config file.

```markdown
+++
description = "A nice description for this blogpost"
socialImage = "path/to/an/image/that/describes/this/post/best"
tags = ["this", "blog", "rocks!"]
+++
```

### Hugo Redirect
A theme component to enable easy redirection in Hugo sites.

#### About

Hugo Redirect enables easy redirection: one of the major pieces missing from Hugo's impressive feature set.

Let's say you
* Have an Ugly URLs like `yoursite.com/cv.pdf` and you'd much rather point people to `yoursite.com/cv`
* Wrote an awesome post on `yoursite.com/blog/2019/09/08/how_to_add_clis` and you'd like to share it to people quickly at `yoursite.com/cli`

Redirection comes in very handy in these cases.

Hugo Redirect currently supports static meta refresh based redirects, `_redirect` generation for [Netlify](https://netlify.com) and and `.htaccess` (for Apache / Nginx servers) generation.

This is not a standalone theme. It is a [Hugo](https://gohugo.io) theme component (sort of like a plugin) providing easy URL redirect capabilities to Hugo sites. A working demo of this redirection is available on my site at [https://prag.io/cv](https://prag.io/cv).

Contributions welcome! Send your pull request.

#### Usage
In the root of your site repository:

1. Add `hugo-redirect` as a submodule to be able to get upstream changes later
	```sh
    $ git submodule add https://github.com/gcc42/hugo-redirect.git themes/hugo-redirect
    ```
2. Add `hugo-redirect` as the left-most element of the `theme` list variable in your site's or theme's configuration file `config.yaml` or `config.toml`. Example, with `config.yaml`:
    ```yaml
    theme: ["hugo-redirect", "other-components", "my-theme"]
    ```
    or, with `config.toml`,
    ```toml
    theme = ["hugo-redirect", "other-components", "my-theme"]
    ```
3. To add a new redirect rule, simply run (It's not recommended to create
   them manually): 
    ```sh
    $ hugo new redirect/cv.md # Replace cv with a (arbitrary) redirect name
    ```
   Open the newly created file `redirect/cv.md` in your editor and update the
   `url` and `redirect_to` fields in the front matter, like so:
   ```toml
   type = "redirect"
   url = "/cv"
   redirect_to = "/cv.pdf"
   redirect_enabled = true
   ``` 
4. If you're hosting on Netlify or Apache/Nginx/<Service that supports `.htaccess`>, follow the steps below to enable `_redirects` file generation (recommended)

#### Things to note
1. I'd recommend enabling the appropriate `_redirects`/`.htaccess` based on where you're hosting. (Even though `meta` redirects work fine, this will potentially improve the speed and help with SEO)
2. Avoid mixing `hugo-redirect` with manual redirection, or you could end up creating a nasty redirect loop
3. Make sure you enter the `url` and `redirect_to` parameters *exactly* as you want them. This means that if you want `/cv --> /cv.pdf`, make sure you set `url = /cv` and NOT `url = /cv/` (however because of the way Hugo works currently, both `/cv --> /cv.pdf` and `/cv/ --> /cv.pdf` will be set up)
