<template>
  <leftNav v-if="menus">
    <template slot="navbar">
      <topBar :hideLogo="true" />
    </template>

    <template slot="left">
      <sidebar class="sidebar">
        <sec v-for="menu in (menus)" :name="menu.label" :key="menu.label">
          <item v-for="m in (menu.items || [])" :key="m.label" :name="m.label" :to="m.to" :items="m.items"/>
        </sec>
      </sidebar>
    </template>

    <template slot="body">
      <component class="markdown" :is="content" />
    </template>
  </leftNav>

  <div v-else class="container">
    <component class="markdown" :is="content" />
    <imprint class="imprint" :horizontal="true" />
  </div>
</template>

<script lang="ts">
import { Component, Vue } from "nuxt-property-decorator";
import { Context } from "@nuxt/types";

import leftNav from "@/components/pages/navbar-left.vue";
import topBar from "@/components/pages/topbar.vue";

import sidebar from "@/components/sidebar/bar.vue";
import item from "@/components/sidebar/item.vue";
import sec from "@/components/sidebar/section.vue";

import faq from "@/components/faq.vue";
import sponsor from "@/components/about/sponsor.vue";
import pe from "@/components/about/pe.vue";
import members from "@/components/about/members.vue";
import imprint from "@/components/imprint.vue";

import panel from "@/components/layout/panel.vue";
import block from "@/components/layout/block.vue";

import bulletPoint from "@/components/process/bulletPoint.vue";
import processPanel from "@/components/process/panel.vue";
import headline from "@/components/process/headline.vue";
import numeration from "@/components/process/numeration.vue";
import numerationItem from "@/components/process/numeration-item.vue";

import {ComponentName} from "@/constants/componentName";
import {IMenuItem} from "@/constants/interfaces/MenuItem";

@Component({
  name: ComponentName.PagesInfo,
  components: {
    sidebar,
    item,
    sec,
    leftNav,
    topBar,
    imprint,
    pe,
    members
  },
})
export default class extends Vue {
  title: string = "";
  seo: string = "";
  description: string = "";
  content: string = "";
  menus: IMenuItem[] | null = null;

  layout(context: Context) {
    const content = require(`@/content/${context.params.pathMatch}.md`);

    return content.attributes?.layout
      ? content.attributes?.layout
      : content.attributes?.menu != null
        ? 'main-left'
        : 'default';
  }

  head() {
    return {
      title: this.seo,
      meta: [
        {
          hid: "description",
          name: "description",
          content: this.description
        }
      ]
    };
  }

  created() {
    this.$store.commit('support/context', `zu '${this.title}'`);
  }

  async asyncData(context: Context) {
    try {
      let content = await import(`@/content/${context.params.pathMatch}.md`);

      const other = {
        extends: content.vue.component,
        components: {
          block,
          bulletPoint,
          faq,
          headline,
          members,
          numeration,
          numerationItem,
          panel,
          pe,
          processPanel,
          sponsor,
        }
      };


      let menus = content.attributes?.menu;

      if (menus != null && menus.length == null) {
        menus = [menus];
      }

      return {
        nav: content.attributes?.nav != false,
        title: content.attributes?.title,
        description: content.attributes?.description,
        seo: content.attributes?.seo || content.attributes?.title,
        content: other,
        menus,
      };
    } catch (e) {
      context.error({
        statusCode: 404,
        message: context.app.i18n.t('errorpage.notfound') as string
      });
    }
  }
}
</script>

<style lang="scss" scoped>
@import "@/assets/scales";
@import "./markdown.scss";

.sidebar {
  display: flex;
}

.imprint {
  margin-left: -$gridsize;
  padding-bottom: 10px;
}

.container {
  -ms-overflow-style: none;
  -webkit-overflow-scrolling: touch;
  display: block;
  height: calc(100vh - #{$pageHeaderHeight});
  overflow-y: scroll;
  padding: $gridsize $gridsize 0;
}

@media only screen and (max-width: $breakpoint_vl) {
  .container {
    padding-left: $pageMarginMin;
    padding-right: $pageMarginMin;
  }
}
</style>
