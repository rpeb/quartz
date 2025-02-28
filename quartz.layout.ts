import { PageLayout, SharedLayout } from "./quartz/cfg"
import * as Component from "./quartz/components"
import 'dotenv/config';
import { SimpleSlug } from "./quartz/util/path"
const myRepoID = process.env.GISCUS_REPO_ID;
const myCategoryID = process.env.GISCUS_CATEGORY_ID;

// components shared across all pages
export const sharedPageComponents: SharedLayout = {
  head: Component.Head(),
  header: [],
  afterBody: [
    Component._OnlyFor(
      { titles: ["PD's Digital Notebook"] },
      Component.RecentNotes({
        showTags: true,
        title: "Recently added notes:",
        showDate: true,
        limit: 5,
      }),
    ),
    Component.Comments({
      provider: "giscus",
      options: {
        // from data-repo
        repo: "rpeb/quartz",
        // from data-repo-id
        repoId: myRepoID,
        // from data-category
        category: "General",
        // from data-category-id
        categoryId: myCategoryID,
      },
    }),
  ],
  footer: Component.Footer({
    links: {},
  }),
}

// components for pages that display a single page (e.g. a single note)
export const defaultContentPageLayout: PageLayout = {
  beforeBody: [
    Component.Breadcrumbs(),
    Component.ArticleTitle(),
    Component.ContentMeta(),
    Component.TagList(),
  ],
  left: [
    Component.PageTitle(),
    Component.MobileOnly(Component.Spacer()),
    Component.Search(),
    Component.Darkmode(),
    Component.Explorer(),
    Component.DesktopOnly(
      Component.RecentNotes({
        title: "Recent Writing",
        limit: 4,
        filter: (f) =>
          f.slug!.startsWith("posts/") && f.slug! !== "posts/index" && !f.frontmatter?.noindex,
        linkToMore: "posts/" as SimpleSlug,
      }),
    ),
    Component.DesktopOnly(
      Component.RecentNotes({
        title: "Recent Notes",
        limit: 2,
        filter: (f) => f.slug!.startsWith("thoughts/"),
        linkToMore: "thoughts/" as SimpleSlug,
      }),
    ),
    Component.DesktopOnly(Component.TableOfContents()),
  ],
  right: [
    Component.Graph({
      localGraph: {
        showTags: false,
      },
      globalGraph: {
        showTags: false,
      },
    }),
    Component.DesktopOnly(Component.TableOfContents()),
    Component.Backlinks(),
  ],
}

// components for pages that display lists of pages  (e.g. tags or folders)
export const defaultListPageLayout: PageLayout = {
  beforeBody: [Component.Breadcrumbs(), Component.ArticleTitle(), Component.ContentMeta()],
  left: [
    Component.PageTitle(),
    Component.MobileOnly(Component.Spacer()),
    Component.Search(),
    Component.Darkmode(),
    Component.Explorer(),
  ],
  right: [],
}
