export type Language = "en" | "zh" | "fr" | "es" | "de";

export interface Translations {
  // Navigation
  nav: {
    dashboard: string;
    credentials: string;
    settings: string;
  };
  
  // Common
  common: {
    save: string;
    cancel: string;
    reset: string;
    loading: string;
    saving: string;
    error: string;
    success: string;
    close: string;
    apply: string;
    delete: string;
    edit: string;
    add: string;
    remove: string;
    search: string;
    filter: string;
    select: string;
    selected: string;
    all: string;
    none: string;
    poweredBy: string;
  };

  // Settings Page
  settings: {
    title: string;
    description: string;
    language: string;
    languageDescription: string;
    theme: string;
    themeDescription: string;
    riskFlagThresholds: string;
    riskFlagThresholdsDescription: string;
    averageTrendWeights: string;
    averageTrendWeightsDescription: string;
    noActivityThreshold: string;
    noActivityThresholdDescription: string;
    stalePrThreshold: string;
    stalePrThresholdDescription: string;
    singleContributorRisk: string;
    singleContributorRiskDescription: string;
    commitsWeight: string;
    commitsWeightDescription: string;
    prsOpenedWeight: string;
    prsOpenedWeightDescription: string;
    prsMergedWeight: string;
    prsMergedWeightDescription: string;
    issuesClosedWeight: string;
    issuesClosedWeightDescription: string;
    resetToDefaults: string;
    saveChanges: string;
    howAverageTrendWorks: string;
    averageTrendFormula: string;
    averageTrendExplanation: string;
    days: string;
    percent: string;
    min: string;
    max: string;
    default: string;
  };

  // Dashboard Page
  dashboard: {
    title: string;
    teamSummary: string;
    totalCommits: string;
    totalPrsOpened: string;
    totalPrsMerged: string;
    totalIssuesClosed: string;
    averageTrend: string;
    internalCommits: string;
    externalCommits: string;
    internalPercentage: string;
    externalPercentage: string;
    repositorySummaries: string;
    riskFlags: string;
    contributors: string;
    lastSynced: string;
    neverSynced: string;
    syncNow: string;
    syncing: string;
    selectTimeRange: string;
    last7Days: string;
    last30Days: string;
    last90Days: string;
    allTime: string;
    custom: string;
    selectContributor: string;
    allContributors: string;
    highRisk: string;
    mediumRisk: string;
    lowRisk: string;
    noRiskFlags: string;
    noContributors: string;
    noRepositories: string;
    dailyCommits: string;
    weeklyReport: string;
    noReportAvailable: string;
    syncDataToGenerateReport: string;
    internal: string;
    external: string;
    commits: string;
    prsOpened: string;
    prsMerged: string;
    issuesClosed: string;
    trend: string;
    positive: string;
    negative: string;
    neutral: string;
    inactive: string;
    stalePr: string;
    singleContributor: string;
    viewOnGitHub: string;
    linkedin: string;
    twitter: string;
    website: string;
  };

  // Credentials Page
  credentials: {
    title: string;
    githubPat: string;
    githubPatDescription: string;
    patConfigured: string;
    authenticatedAs: string;
    enterPat: string;
    storeMode: string;
    encrypted: string;
    memory: string;
    memoryDescription: string;
    encryptedDescription: string;
    submitPat: string;
    submitUsername: string;
    enterUsername: string;
    teamMembers: string;
    teamMembersDescription: string;
    addTeamMember: string;
    externalContributors: string;
    externalContributorsDescription: string;
    addExternalContributor: string;
    internalOrganizations: string;
    internalOrganizationsDescription: string;
    addOrganization: string;
    selectedRepositories: string;
    selectedRepositoriesDescription: string;
    selectRepositories: string;
    noRepositoriesSelected: string;
    syncRepositories: string;
    showPat: string;
    hidePat: string;
    deletePat: string;
    deletePatConfirm: string;
  };
}

export const translations: Record<Language, Translations> = {
  en: {
    nav: {
      dashboard: "Dashboard",
      credentials: "Credentials",
      settings: "Settings",
    },
    common: {
      save: "Save",
      cancel: "Cancel",
      reset: "Reset",
      loading: "Loading...",
      saving: "Saving...",
      error: "Error",
      success: "Success",
      close: "Close",
      apply: "Apply",
      delete: "Delete",
      edit: "Edit",
      add: "Add",
      remove: "Remove",
      search: "Search",
      filter: "Filter",
      select: "Select",
      selected: "Selected",
      all: "All",
      none: "None",
      poweredBy: "Powered by",
    },
    settings: {
      title: "Settings",
      description: "Configure risk thresholds and average trend calculation weights",
      language: "Language",
      languageDescription: "Choose your preferred language",
      theme: "Theme",
      themeDescription: "Choose your accent color to customize the appearance",
      riskFlagThresholds: "Risk Flag Thresholds",
      riskFlagThresholdsDescription: "Configure when alerts should be triggered based on team activity",
      averageTrendWeights: "Average Trend Weights",
      averageTrendWeightsDescription: "Adjust the importance of different metrics in the average trend calculation",
      noActivityThreshold: "No Activity Threshold",
      noActivityThresholdDescription: "Days without commits before flagging as inactive",
      stalePrThreshold: "Stale PR Threshold",
      stalePrThresholdDescription: "Days before an open PR is considered stale",
      singleContributorRisk: "Single Contributor Risk %",
      singleContributorRiskDescription: "Percentage of work by one person before flagging",
      commitsWeight: "Commits Weight",
      commitsWeightDescription: "Weight for commits in average trend calculation",
      prsOpenedWeight: "PRs Opened Weight",
      prsOpenedWeightDescription: "Weight for opened PRs in average trend calculation",
      prsMergedWeight: "PRs Merged Weight",
      prsMergedWeightDescription: "Weight for merged PRs in average trend calculation",
      issuesClosedWeight: "Issues Closed Weight",
      issuesClosedWeightDescription: "Weight for closed issues in average trend calculation",
      resetToDefaults: "Reset to Defaults",
      saveChanges: "Save Changes",
      howAverageTrendWorks: "How Average Trend Works",
      averageTrendFormula: "Daily Weighted Score = (Commits × {commits}) + (PRs Opened × {prsOpened}) + (PRs Merged × {prsMerged}) + (Issues Closed × {issuesClosed})",
      averageTrendExplanation: "The average trend is calculated using least squares regression on daily weighted scores over time. A positive trend indicates increasing activity, negative indicates decreasing activity. Higher weights give more importance to that metric. Merged PRs typically have the highest weight as they represent completed, reviewed work.",
      days: "days",
      percent: "%",
      min: "Min",
      max: "Max",
      default: "Default",
    },
    dashboard: {
      title: "Dashboard",
      teamSummary: "Team Summary",
      totalCommits: "Total Commits",
      totalPrsOpened: "Total PRs Opened",
      totalPrsMerged: "Total PRs Merged",
      totalIssuesClosed: "Total Issues Closed",
      averageTrend: "Average Trend",
      internalCommits: "Internal Commits",
      externalCommits: "External Commits",
      internalPercentage: "Internal %",
      externalPercentage: "External %",
      repositorySummaries: "Repository Summaries",
      riskFlags: "Risk Flags",
      contributors: "Contributors",
      lastSynced: "Last Synced",
      neverSynced: "Never Synced",
      syncNow: "Sync Now",
      syncing: "Syncing...",
      selectTimeRange: "Select Time Range",
      last7Days: "Last 7 Days",
      last30Days: "Last 30 Days",
      last90Days: "Last 90 Days",
      allTime: "All Time",
      custom: "Custom",
      selectContributor: "Select Contributor",
      allContributors: "All Contributors",
      highRisk: "High Risk",
      mediumRisk: "Medium Risk",
      lowRisk: "Low Risk",
      noRiskFlags: "No risk flags found",
      noContributors: "No contributors found",
      noRepositories: "No repositories found",
      dailyCommits: "Daily Commits",
      weeklyReport: "Weekly Report",
      noReportAvailable: "No report available yet",
      syncDataToGenerateReport: "Sync data to generate a report",
      internal: "Internal",
      external: "External",
      commits: "Commits",
      prsOpened: "PRs Opened",
      prsMerged: "PRs Merged",
      issuesClosed: "Issues Closed",
      trend: "Trend",
      positive: "Positive",
      negative: "Negative",
      neutral: "Neutral",
      inactive: "Inactive",
      stalePr: "Stale PR",
      singleContributor: "Single Contributor",
      viewOnGitHub: "View on GitHub",
      linkedin: "LinkedIn",
      twitter: "Twitter",
      website: "Website",
    },
    credentials: {
      title: "Credentials",
      githubPat: "GitHub Personal Access Token",
      githubPatDescription: "We will not store your PAT without your permission, your PAT will be deleted after each session",
      patConfigured: "PAT Configured",
      authenticatedAs: "Authenticated as",
      enterPat: "Enter PAT",
      storeMode: "Store Mode",
      encrypted: "Encrypted",
      memory: "Memory",
      memoryDescription: "PAT stored in memory only (cleared on refresh)",
      encryptedDescription: "PAT encrypted and stored securely",
      submitPat: "Submit PAT",
      submitUsername: "Submit Username",
      enterUsername: "Enter GitHub Username",
      teamMembers: "Team Members",
      teamMembersDescription: "Add GitHub usernames of your team members",
      addTeamMember: "Add Team Member",
      externalContributors: "External Contributors",
      externalContributorsDescription: "Add GitHub usernames of external contributors",
      addExternalContributor: "Add External Contributor",
      internalOrganizations: "Internal Organizations",
      internalOrganizationsDescription: "Add GitHub organizations to mark as internal",
      addOrganization: "Add Organization",
      selectedRepositories: "Selected Repositories",
      selectedRepositoriesDescription: "Select repositories to track",
      selectRepositories: "Select Repositories",
      noRepositoriesSelected: "No repositories selected",
      syncRepositories: "Sync Repositories",
      showPat: "Show PAT",
      hidePat: "Hide PAT",
      deletePat: "Delete PAT",
      deletePatConfirm: "Are you sure you want to delete your PAT?",
    },
  },
  zh: {
    nav: {
      dashboard: "仪表板",
      credentials: "凭证",
      settings: "设置",
    },
    common: {
      save: "保存",
      cancel: "取消",
      reset: "重置",
      loading: "加载中...",
      saving: "保存中...",
      error: "错误",
      success: "成功",
      close: "关闭",
      apply: "应用",
      delete: "删除",
      edit: "编辑",
      add: "添加",
      remove: "移除",
      search: "搜索",
      filter: "筛选",
      select: "选择",
      selected: "已选择",
      all: "全部",
      none: "无",
      poweredBy: "由",
    },
    settings: {
      title: "设置",
      description: "配置风险阈值和平均趋势计算权重",
      language: "语言",
      languageDescription: "选择您的首选语言",
      theme: "主题",
      themeDescription: "选择您的强调色以自定义外观",
      riskFlagThresholds: "风险标志阈值",
      riskFlagThresholdsDescription: "根据团队活动配置何时触发警报",
      averageTrendWeights: "平均趋势权重",
      averageTrendWeightsDescription: "调整不同指标在平均趋势计算中的重要性",
      noActivityThreshold: "无活动阈值",
      noActivityThresholdDescription: "标记为不活跃之前没有提交的天数",
      stalePrThreshold: "过时PR阈值",
      stalePrThresholdDescription: "开放PR被视为过时之前的天数",
      singleContributorRisk: "单一贡献者风险 %",
      singleContributorRiskDescription: "标记之前一个人完成工作的百分比",
      commitsWeight: "提交权重",
      commitsWeightDescription: "提交在平均趋势计算中的权重",
      prsOpenedWeight: "已打开PR权重",
      prsOpenedWeightDescription: "已打开PR在平均趋势计算中的权重",
      prsMergedWeight: "已合并PR权重",
      prsMergedWeightDescription: "已合并PR在平均趋势计算中的权重",
      issuesClosedWeight: "已关闭问题权重",
      issuesClosedWeightDescription: "已关闭问题在平均趋势计算中的权重",
      resetToDefaults: "重置为默认值",
      saveChanges: "保存更改",
      howAverageTrendWorks: "平均趋势如何工作",
      averageTrendFormula: "每日加权分数 = (提交 × {commits}) + (已打开PR × {prsOpened}) + (已合并PR × {prsMerged}) + (已关闭问题 × {issuesClosed})",
      averageTrendExplanation: "平均趋势是使用最小二乘回归对一段时间内的每日加权分数计算的。正趋势表示活动增加，负趋势表示活动减少。更高的权重使该指标更重要。已合并的PR通常具有最高权重，因为它们代表已完成、已审查的工作。",
      days: "天",
      percent: "%",
      min: "最小",
      max: "最大",
      default: "默认",
    },
    dashboard: {
      title: "仪表板",
      teamSummary: "团队摘要",
      totalCommits: "总提交数",
      totalPrsOpened: "总打开PR数",
      totalPrsMerged: "总合并PR数",
      totalIssuesClosed: "总关闭问题数",
      averageTrend: "平均趋势",
      internalCommits: "内部提交",
      externalCommits: "外部提交",
      internalPercentage: "内部 %",
      externalPercentage: "外部 %",
      repositorySummaries: "仓库摘要",
      riskFlags: "风险标志",
      contributors: "贡献者",
      lastSynced: "最后同步",
      neverSynced: "从未同步",
      syncNow: "立即同步",
      syncing: "同步中...",
      selectTimeRange: "选择时间范围",
      last7Days: "最近7天",
      last30Days: "最近30天",
      last90Days: "最近90天",
      allTime: "全部时间",
      custom: "自定义",
      selectContributor: "选择贡献者",
      allContributors: "所有贡献者",
      highRisk: "高风险",
      mediumRisk: "中等风险",
      lowRisk: "低风险",
      noRiskFlags: "未找到风险标志",
      noContributors: "未找到贡献者",
      noRepositories: "未找到仓库",
      dailyCommits: "每日提交",
      weeklyReport: "周报",
      noReportAvailable: "尚无报告",
      syncDataToGenerateReport: "同步数据以生成报告",
      internal: "内部",
      external: "外部",
      commits: "提交",
      prsOpened: "已打开PR",
      prsMerged: "已合并PR",
      issuesClosed: "已关闭问题",
      trend: "趋势",
      positive: "正向",
      negative: "负向",
      neutral: "中性",
      inactive: "不活跃",
      stalePr: "过时PR",
      singleContributor: "单一贡献者",
      viewOnGitHub: "在GitHub上查看",
      linkedin: "领英",
      twitter: "推特",
      website: "网站",
    },
    credentials: {
      title: "凭证",
      githubPat: "GitHub个人访问令牌",
      githubPatDescription: "未经您的许可，我们不会存储您的PAT，您的PAT将在每次会话后删除",
      patConfigured: "PAT已配置",
      authenticatedAs: "认证为",
      enterPat: "输入PAT",
      storeMode: "存储模式",
      encrypted: "加密",
      memory: "内存",
      memoryDescription: "PAT仅存储在内存中（刷新时清除）",
      encryptedDescription: "PAT已加密并安全存储",
      submitPat: "提交PAT",
      submitUsername: "提交用户名",
      enterUsername: "输入GitHub用户名",
      teamMembers: "团队成员",
      teamMembersDescription: "添加您团队成员的GitHub用户名",
      addTeamMember: "添加团队成员",
      externalContributors: "外部贡献者",
      externalContributorsDescription: "添加外部贡献者的GitHub用户名",
      addExternalContributor: "添加外部贡献者",
      internalOrganizations: "内部组织",
      internalOrganizationsDescription: "添加GitHub组织以标记为内部",
      addOrganization: "添加组织",
      selectedRepositories: "选定的仓库",
      selectedRepositoriesDescription: "选择要跟踪的仓库",
      selectRepositories: "选择仓库",
      noRepositoriesSelected: "未选择仓库",
      syncRepositories: "同步仓库",
      showPat: "显示PAT",
      hidePat: "隐藏PAT",
      deletePat: "删除PAT",
      deletePatConfirm: "您确定要删除您的PAT吗？",
    },
  },
  fr: {
    nav: {
      dashboard: "Tableau de bord",
      credentials: "Identifiants",
      settings: "Paramètres",
    },
    common: {
      save: "Enregistrer",
      cancel: "Annuler",
      reset: "Réinitialiser",
      loading: "Chargement...",
      saving: "Enregistrement...",
      error: "Erreur",
      success: "Succès",
      close: "Fermer",
      apply: "Appliquer",
      delete: "Supprimer",
      edit: "Modifier",
      add: "Ajouter",
      remove: "Retirer",
      search: "Rechercher",
      filter: "Filtrer",
      select: "Sélectionner",
      selected: "Sélectionné",
      all: "Tout",
      none: "Aucun",
      poweredBy: "Propulsé par",
    },
    settings: {
      title: "Paramètres",
      description: "Configurer les seuils de risque et les poids de calcul de tendance moyenne",
      language: "Langue",
      languageDescription: "Choisissez votre langue préférée",
      theme: "Thème",
      themeDescription: "Choisissez votre couleur d'accent pour personnaliser l'apparence",
      riskFlagThresholds: "Seuils d'alerte de risque",
      riskFlagThresholdsDescription: "Configurer quand les alertes doivent être déclenchées en fonction de l'activité de l'équipe",
      averageTrendWeights: "Poids de tendance moyenne",
      averageTrendWeightsDescription: "Ajuster l'importance des différentes métriques dans le calcul de tendance moyenne",
      noActivityThreshold: "Seuil d'inactivité",
      noActivityThresholdDescription: "Jours sans commits avant de signaler comme inactif",
      stalePrThreshold: "Seuil de PR obsolète",
      stalePrThresholdDescription: "Jours avant qu'une PR ouverte ne soit considérée comme obsolète",
      singleContributorRisk: "Risque de contributeur unique %",
      singleContributorRiskDescription: "Pourcentage de travail par une personne avant de signaler",
      commitsWeight: "Poids des commits",
      commitsWeightDescription: "Poids des commits dans le calcul de tendance moyenne",
      prsOpenedWeight: "Poids des PR ouvertes",
      prsOpenedWeightDescription: "Poids des PR ouvertes dans le calcul de tendance moyenne",
      prsMergedWeight: "Poids des PR fusionnées",
      prsMergedWeightDescription: "Poids des PR fusionnées dans le calcul de tendance moyenne",
      issuesClosedWeight: "Poids des problèmes fermés",
      issuesClosedWeightDescription: "Poids des problèmes fermés dans le calcul de tendance moyenne",
      resetToDefaults: "Réinitialiser aux valeurs par défaut",
      saveChanges: "Enregistrer les modifications",
      howAverageTrendWorks: "Comment fonctionne la tendance moyenne",
      averageTrendFormula: "Score pondéré quotidien = (Commits × {commits}) + (PR ouvertes × {prsOpened}) + (PR fusionnées × {prsMerged}) + (Problèmes fermés × {issuesClosed})",
      averageTrendExplanation: "La tendance moyenne est calculée en utilisant la régression des moindres carrés sur les scores pondérés quotidiens au fil du temps. Une tendance positive indique une activité croissante, négative indique une activité décroissante. Des poids plus élevés donnent plus d'importance à cette métrique. Les PR fusionnées ont généralement le poids le plus élevé car elles représentent un travail terminé et examiné.",
      days: "jours",
      percent: "%",
      min: "Min",
      max: "Max",
      default: "Par défaut",
    },
    dashboard: {
      title: "Tableau de bord",
      teamSummary: "Résumé de l'équipe",
      totalCommits: "Total des commits",
      totalPrsOpened: "Total des PR ouvertes",
      totalPrsMerged: "Total des PR fusionnées",
      totalIssuesClosed: "Total des problèmes fermés",
      averageTrend: "Tendance moyenne",
      internalCommits: "Commits internes",
      externalCommits: "Commits externes",
      internalPercentage: "Interne %",
      externalPercentage: "Externe %",
      repositorySummaries: "Résumés des dépôts",
      riskFlags: "Alertes de risque",
      contributors: "Contributeurs",
      lastSynced: "Dernière synchronisation",
      neverSynced: "Jamais synchronisé",
      syncNow: "Synchroniser maintenant",
      syncing: "Synchronisation...",
      selectTimeRange: "Sélectionner la plage horaire",
      last7Days: "7 derniers jours",
      last30Days: "30 derniers jours",
      last90Days: "90 derniers jours",
      allTime: "Tout le temps",
      custom: "Personnalisé",
      selectContributor: "Sélectionner un contributeur",
      allContributors: "Tous les contributeurs",
      highRisk: "Risque élevé",
      mediumRisk: "Risque moyen",
      lowRisk: "Risque faible",
      noRiskFlags: "Aucune alerte de risque trouvée",
      noContributors: "Aucun contributeur trouvé",
      noRepositories: "Aucun dépôt trouvé",
      dailyCommits: "Commits quotidiens",
      weeklyReport: "Rapport hebdomadaire",
      noReportAvailable: "Aucun rapport disponible pour le moment",
      syncDataToGenerateReport: "Synchroniser les données pour générer un rapport",
      internal: "Interne",
      external: "Externe",
      commits: "Commits",
      prsOpened: "PR ouvertes",
      prsMerged: "PR fusionnées",
      issuesClosed: "Problèmes fermés",
      trend: "Tendance",
      positive: "Positif",
      negative: "Négatif",
      neutral: "Neutre",
      inactive: "Inactif",
      stalePr: "PR obsolète",
      singleContributor: "Contributeur unique",
      viewOnGitHub: "Voir sur GitHub",
      linkedin: "LinkedIn",
      twitter: "Twitter",
      website: "Site web",
    },
    credentials: {
      title: "Identifiants",
      githubPat: "Jeton d'accès personnel GitHub",
      githubPatDescription: "Nous ne stockerons pas votre PAT sans votre permission, votre PAT sera supprimé après chaque session",
      patConfigured: "PAT configuré",
      authenticatedAs: "Authentifié en tant que",
      enterPat: "Entrer le PAT",
      storeMode: "Mode de stockage",
      encrypted: "Chiffré",
      memory: "Mémoire",
      memoryDescription: "PAT stocké uniquement en mémoire (effacé lors du rafraîchissement)",
      encryptedDescription: "PAT chiffré et stocké en toute sécurité",
      submitPat: "Soumettre le PAT",
      submitUsername: "Soumettre le nom d'utilisateur",
      enterUsername: "Entrer le nom d'utilisateur GitHub",
      teamMembers: "Membres de l'équipe",
      teamMembersDescription: "Ajouter les noms d'utilisateur GitHub de vos membres d'équipe",
      addTeamMember: "Ajouter un membre d'équipe",
      externalContributors: "Contributeurs externes",
      externalContributorsDescription: "Ajouter les noms d'utilisateur GitHub des contributeurs externes",
      addExternalContributor: "Ajouter un contributeur externe",
      internalOrganizations: "Organisations internes",
      internalOrganizationsDescription: "Ajouter des organisations GitHub à marquer comme internes",
      addOrganization: "Ajouter une organisation",
      selectedRepositories: "Dépôts sélectionnés",
      selectedRepositoriesDescription: "Sélectionner les dépôts à suivre",
      selectRepositories: "Sélectionner les dépôts",
      noRepositoriesSelected: "Aucun dépôt sélectionné",
      syncRepositories: "Synchroniser les dépôts",
      showPat: "Afficher le PAT",
      hidePat: "Masquer le PAT",
      deletePat: "Supprimer le PAT",
      deletePatConfirm: "Êtes-vous sûr de vouloir supprimer votre PAT ?",
    },
  },
  es: {
    nav: {
      dashboard: "Panel de control",
      credentials: "Credenciales",
      settings: "Configuración",
    },
    common: {
      save: "Guardar",
      cancel: "Cancelar",
      reset: "Restablecer",
      loading: "Cargando...",
      saving: "Guardando...",
      error: "Error",
      success: "Éxito",
      close: "Cerrar",
      apply: "Aplicar",
      delete: "Eliminar",
      edit: "Editar",
      add: "Agregar",
      remove: "Quitar",
      search: "Buscar",
      filter: "Filtrar",
      select: "Seleccionar",
      selected: "Seleccionado",
      all: "Todo",
      none: "Ninguno",
      poweredBy: "Desarrollado por",
    },
    settings: {
      title: "Configuración",
      description: "Configurar umbrales de riesgo y pesos de cálculo de tendencia promedio",
      language: "Idioma",
      languageDescription: "Elija su idioma preferido",
      theme: "Tema",
      themeDescription: "Elija su color de acento para personalizar la apariencia",
      riskFlagThresholds: "Umbrales de alerta de riesgo",
      riskFlagThresholdsDescription: "Configurar cuándo se deben activar las alertas según la actividad del equipo",
      averageTrendWeights: "Pesos de tendencia promedio",
      averageTrendWeightsDescription: "Ajustar la importancia de diferentes métricas en el cálculo de tendencia promedio",
      noActivityThreshold: "Umbral de inactividad",
      noActivityThresholdDescription: "Días sin commits antes de marcar como inactivo",
      stalePrThreshold: "Umbral de PR obsoleta",
      stalePrThresholdDescription: "Días antes de que una PR abierta se considere obsoleta",
      singleContributorRisk: "Riesgo de contribuidor único %",
      singleContributorRiskDescription: "Porcentaje de trabajo por una persona antes de marcar",
      commitsWeight: "Peso de commits",
      commitsWeightDescription: "Peso de commits en el cálculo de tendencia promedio",
      prsOpenedWeight: "Peso de PR abiertas",
      prsOpenedWeightDescription: "Peso de PR abiertas en el cálculo de tendencia promedio",
      prsMergedWeight: "Peso de PR fusionadas",
      prsMergedWeightDescription: "Peso de PR fusionadas en el cálculo de tendencia promedio",
      issuesClosedWeight: "Peso de problemas cerrados",
      issuesClosedWeightDescription: "Peso de problemas cerrados en el cálculo de tendencia promedio",
      resetToDefaults: "Restablecer a valores predeterminados",
      saveChanges: "Guardar cambios",
      howAverageTrendWorks: "Cómo funciona la tendencia promedio",
      averageTrendFormula: "Puntuación ponderada diaria = (Commits × {commits}) + (PR abiertas × {prsOpened}) + (PR fusionadas × {prsMerged}) + (Problemas cerrados × {issuesClosed})",
      averageTrendExplanation: "La tendencia promedio se calcula usando regresión de mínimos cuadrados en puntuaciones ponderadas diarias a lo largo del tiempo. Una tendencia positiva indica actividad creciente, negativa indica actividad decreciente. Pesos más altos dan más importancia a esa métrica. Las PR fusionadas típicamente tienen el peso más alto ya que representan trabajo completado y revisado.",
      days: "días",
      percent: "%",
      min: "Mín",
      max: "Máx",
      default: "Predeterminado",
    },
    dashboard: {
      title: "Panel de control",
      teamSummary: "Resumen del equipo",
      totalCommits: "Total de commits",
      totalPrsOpened: "Total de PR abiertas",
      totalPrsMerged: "Total de PR fusionadas",
      totalIssuesClosed: "Total de problemas cerrados",
      averageTrend: "Tendencia promedio",
      internalCommits: "Commits internos",
      externalCommits: "Commits externos",
      internalPercentage: "Interno %",
      externalPercentage: "Externo %",
      repositorySummaries: "Resúmenes de repositorios",
      riskFlags: "Alertas de riesgo",
      contributors: "Contribuidores",
      lastSynced: "Última sincronización",
      neverSynced: "Nunca sincronizado",
      syncNow: "Sincronizar ahora",
      syncing: "Sincronizando...",
      selectTimeRange: "Seleccionar rango de tiempo",
      last7Days: "Últimos 7 días",
      last30Days: "Últimos 30 días",
      last90Days: "Últimos 90 días",
      allTime: "Todo el tiempo",
      custom: "Personalizado",
      selectContributor: "Seleccionar contribuidor",
      allContributors: "Todos los contribuidores",
      highRisk: "Riesgo alto",
      mediumRisk: "Riesgo medio",
      lowRisk: "Riesgo bajo",
      noRiskFlags: "No se encontraron alertas de riesgo",
      noContributors: "No se encontraron contribuidores",
      noRepositories: "No se encontraron repositorios",
      dailyCommits: "Commits diarios",
      weeklyReport: "Informe semanal",
      noReportAvailable: "Aún no hay informe disponible",
      syncDataToGenerateReport: "Sincronizar datos para generar un informe",
      internal: "Interno",
      external: "External",
      commits: "Commits",
      prsOpened: "PR abiertas",
      prsMerged: "PR fusionadas",
      issuesClosed: "Problemas cerrados",
      trend: "Tendencia",
      positive: "Positivo",
      negative: "Negativo",
      neutral: "Neutro",
      inactive: "Inactivo",
      stalePr: "PR obsoleta",
      singleContributor: "Contribuidor único",
      viewOnGitHub: "Ver en GitHub",
      linkedin: "LinkedIn",
      twitter: "Twitter",
      website: "Sitio web",
    },
    credentials: {
      title: "Credenciales",
      githubPat: "Token de acceso personal de GitHub",
      githubPatDescription: "No almacenaremos su PAT sin su permiso, su PAT se eliminará después de cada sesión",
      patConfigured: "PAT configurado",
      authenticatedAs: "Autenticado como",
      enterPat: "Ingresar PAT",
      storeMode: "Modo de almacenamiento",
      encrypted: "Cifrado",
      memory: "Memoria",
      memoryDescription: "PAT almacenado solo en memoria (se borra al actualizar)",
      encryptedDescription: "PAT cifrado y almacenado de forma segura",
      submitPat: "Enviar PAT",
      submitUsername: "Enviar nombre de usuario",
      enterUsername: "Ingresar nombre de usuario de GitHub",
      teamMembers: "Miembros del equipo",
      teamMembersDescription: "Agregar nombres de usuario de GitHub de sus miembros del equipo",
      addTeamMember: "Agregar miembro del equipo",
      externalContributors: "Contribuidores externos",
      externalContributorsDescription: "Agregar nombres de usuario de GitHub de contribuidores externos",
      addExternalContributor: "Agregar contribuidor externo",
      internalOrganizations: "Organizaciones internas",
      internalOrganizationsDescription: "Agregar organizaciones de GitHub para marcar como internas",
      addOrganization: "Agregar organización",
      selectedRepositories: "Repositorios seleccionados",
      selectedRepositoriesDescription: "Seleccionar repositorios para rastrear",
      selectRepositories: "Seleccionar repositorios",
      noRepositoriesSelected: "No se seleccionaron repositorios",
      syncRepositories: "Sincronizar repositorios",
      showPat: "Mostrar PAT",
      hidePat: "Ocultar PAT",
      deletePat: "Eliminar PAT",
      deletePatConfirm: "¿Está seguro de que desea eliminar su PAT?",
    },
  },
  de: {
    nav: {
      dashboard: "Dashboard",
      credentials: "Anmeldedaten",
      settings: "Einstellungen",
    },
    common: {
      save: "Speichern",
      cancel: "Abbrechen",
      reset: "Zurücksetzen",
      loading: "Lädt...",
      saving: "Speichert...",
      error: "Fehler",
      success: "Erfolg",
      close: "Schließen",
      apply: "Anwenden",
      delete: "Löschen",
      edit: "Bearbeiten",
      add: "Hinzufügen",
      remove: "Entfernen",
      search: "Suchen",
      filter: "Filtern",
      select: "Auswählen",
      selected: "Ausgewählt",
      all: "Alle",
      none: "Keine",
      poweredBy: "Unterstützt von",
    },
    settings: {
      title: "Einstellungen",
      description: "Risikoschwellen und Gewichtungen für die Durchschnittstrendberechnung konfigurieren",
      language: "Sprache",
      languageDescription: "Wählen Sie Ihre bevorzugte Sprache",
      theme: "Design",
      themeDescription: "Wählen Sie Ihre Akzentfarbe, um das Erscheinungsbild anzupassen",
      riskFlagThresholds: "Risiko-Flag-Schwellen",
      riskFlagThresholdsDescription: "Konfigurieren Sie, wann Warnungen basierend auf der Teamaktivität ausgelöst werden sollen",
      averageTrendWeights: "Durchschnittstrend-Gewichtungen",
      averageTrendWeightsDescription: "Passen Sie die Bedeutung verschiedener Metriken in der Durchschnittstrendberechnung an",
      noActivityThreshold: "Inaktivitätsschwelle",
      noActivityThresholdDescription: "Tage ohne Commits, bevor als inaktiv markiert wird",
      stalePrThreshold: "Veraltete PR-Schwelle",
      stalePrThresholdDescription: "Tage, bevor eine offene PR als veraltet gilt",
      singleContributorRisk: "Einzelbeitragender-Risiko %",
      singleContributorRiskDescription: "Prozentsatz der Arbeit durch eine Person, bevor markiert wird",
      commitsWeight: "Commits-Gewichtung",
      commitsWeightDescription: "Gewichtung für Commits in der Durchschnittstrendberechnung",
      prsOpenedWeight: "Geöffnete PRs-Gewichtung",
      prsOpenedWeightDescription: "Gewichtung für geöffnete PRs in der Durchschnittstrendberechnung",
      prsMergedWeight: "Gemergte PRs-Gewichtung",
      prsMergedWeightDescription: "Gewichtung für gemergte PRs in der Durchschnittstrendberechnung",
      issuesClosedWeight: "Geschlossene Issues-Gewichtung",
      issuesClosedWeightDescription: "Gewichtung für geschlossene Issues in der Durchschnittstrendberechnung",
      resetToDefaults: "Auf Standardwerte zurücksetzen",
      saveChanges: "Änderungen speichern",
      howAverageTrendWorks: "Wie der Durchschnittstrend funktioniert",
      averageTrendFormula: "Tägliche gewichtete Punktzahl = (Commits × {commits}) + (Geöffnete PRs × {prsOpened}) + (Gemergte PRs × {prsMerged}) + (Geschlossene Issues × {issuesClosed})",
      averageTrendExplanation: "Der Durchschnittstrend wird mit der Methode der kleinsten Quadrate auf tägliche gewichtete Punktzahlen über die Zeit berechnet. Ein positiver Trend zeigt steigende Aktivität, negativ zeigt abnehmende Aktivität. Höhere Gewichtungen geben dieser Metrik mehr Bedeutung. Gemergte PRs haben typischerweise die höchste Gewichtung, da sie abgeschlossene, überprüfte Arbeit darstellen.",
      days: "Tage",
      percent: "%",
      min: "Min",
      max: "Max",
      default: "Standard",
    },
    dashboard: {
      title: "Dashboard",
      teamSummary: "Team-Zusammenfassung",
      totalCommits: "Gesamte Commits",
      totalPrsOpened: "Gesamte geöffnete PRs",
      totalPrsMerged: "Gesamte gemergte PRs",
      totalIssuesClosed: "Gesamte geschlossene Issues",
      averageTrend: "Durchschnittstrend",
      internalCommits: "Interne Commits",
      externalCommits: "Externe Commits",
      internalPercentage: "Intern %",
      externalPercentage: "Extern %",
      repositorySummaries: "Repository-Zusammenfassungen",
      riskFlags: "Risiko-Flags",
      contributors: "Beitragende",
      lastSynced: "Zuletzt synchronisiert",
      neverSynced: "Nie synchronisiert",
      syncNow: "Jetzt synchronisieren",
      syncing: "Synchronisiert...",
      selectTimeRange: "Zeitraum auswählen",
      last7Days: "Letzte 7 Tage",
      last30Days: "Letzte 30 Tage",
      last90Days: "Letzte 90 Tage",
      allTime: "Gesamte Zeit",
      custom: "Benutzerdefiniert",
      selectContributor: "Beitragenden auswählen",
      allContributors: "Alle Beitragenden",
      highRisk: "Hohes Risiko",
      mediumRisk: "Mittleres Risiko",
      lowRisk: "Niedriges Risiko",
      noRiskFlags: "Keine Risiko-Flags gefunden",
      noContributors: "Keine Beitragenden gefunden",
      noRepositories: "Keine Repositorys gefunden",
      dailyCommits: "Tägliche Commits",
      weeklyReport: "Wöchentlicher Bericht",
      noReportAvailable: "Noch kein Bericht verfügbar",
      syncDataToGenerateReport: "Daten synchronisieren, um einen Bericht zu generieren",
      internal: "Intern",
      external: "Extern",
      commits: "Commits",
      prsOpened: "Geöffnete PRs",
      prsMerged: "Gemergte PRs",
      issuesClosed: "Geschlossene Issues",
      trend: "Trend",
      positive: "Positiv",
      negative: "Negativ",
      neutral: "Neutral",
      inactive: "Inaktiv",
      stalePr: "Veraltete PR",
      singleContributor: "Einzelbeitragender",
      viewOnGitHub: "Auf GitHub ansehen",
      linkedin: "LinkedIn",
      twitter: "Twitter",
      website: "Website",
    },
    credentials: {
      title: "Anmeldedaten",
      githubPat: "GitHub Personal Access Token",
      githubPatDescription: "Wir speichern Ihren PAT nicht ohne Ihre Erlaubnis, Ihr PAT wird nach jeder Sitzung gelöscht",
      patConfigured: "PAT konfiguriert",
      authenticatedAs: "Authentifiziert als",
      enterPat: "PAT eingeben",
      storeMode: "Speichermodus",
      encrypted: "Verschlüsselt",
      memory: "Speicher",
      memoryDescription: "PAT nur im Speicher gespeichert (wird beim Aktualisieren gelöscht)",
      encryptedDescription: "PAT verschlüsselt und sicher gespeichert",
      submitPat: "PAT übermitteln",
      submitUsername: "Benutzernamen übermitteln",
      enterUsername: "GitHub-Benutzernamen eingeben",
      teamMembers: "Teammitglieder",
      teamMembersDescription: "GitHub-Benutzernamen Ihrer Teammitglieder hinzufügen",
      addTeamMember: "Teammitglied hinzufügen",
      externalContributors: "Externe Beitragende",
      externalContributorsDescription: "GitHub-Benutzernamen externer Beitragender hinzufügen",
      addExternalContributor: "Externen Beitragenden hinzufügen",
      internalOrganizations: "Interne Organisationen",
      internalOrganizationsDescription: "GitHub-Organisationen hinzufügen, die als intern markiert werden sollen",
      addOrganization: "Organisation hinzufügen",
      selectedRepositories: "Ausgewählte Repositorys",
      selectedRepositoriesDescription: "Repositorys zum Verfolgen auswählen",
      selectRepositories: "Repositorys auswählen",
      noRepositoriesSelected: "Keine Repositorys ausgewählt",
      syncRepositories: "Repositorys synchronisieren",
      showPat: "PAT anzeigen",
      hidePat: "PAT ausblenden",
      deletePat: "PAT löschen",
      deletePatConfirm: "Sind Sie sicher, dass Sie Ihren PAT löschen möchten?",
    },
  },
};

export function getTranslation(language: Language): Translations {
  return translations[language] || translations.en;
}
