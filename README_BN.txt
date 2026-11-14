AI Quota Control PWA — v3.0.2

এটি mobile-first, manual AI quota tracking app। এটি provider-এর live quota API বা automatic account sync নয়।

গোপনীয়তা (Privacy)
--------------------
পুরোনো refat247.github.io ঠিকানায় একই browser origin অন্য Pages project-এর সঙ্গে শেয়ার হতে পারে। তাই এই version-এ ওই ঠিকানায় Private JSON import নিষ্ক্রিয় (HOLD)। সেখানে account/email/billing তথ্য manually লিখবেন না। কোনো data leak হয়েছে—এমন প্রমাণ নেই।

Firebase Hosting (Spark)
------------------------
শুধু এই app-এর জন্য আলাদা Firebase project তৈরি করুন। Firebase Hosting ব্যবহার করুন; Firebase App Hosting নয়। Firebase-এর free Spark plan দিয়ে আলাদা SITE_ID.web.app address পাওয়া যায়; project/site ID নিজের account-এ যাচাই করতে হবে। App-এর public source ছাড়া Private JSON Firebase/GitHub-এ upload করবেন না।

Owner-approved code থেকে npm run build:hosting চালালে dist/ folder-এ মাত্র ৫টি public asset থাকবে। তারপর Firebase CLI/Cloud Shell দিয়ে firebase deploy --only hosting --project YOUR_PROJECT_ID চালানো যাবে। Placeholder project ID বদলাতে হবে।

Import ও Save
-------------
Dedicated hostname চালু এবং independent privacy check সম্পন্ন হলে Chrome-এ ওই URL খুলবেন। Backup → Import JSON file অথবা Paste JSON বেছে নিন। আগের data থাকলে আগে Export private JSON backup করুন; import আগের data replace করে। Paste করার পর field পরিষ্কার হয়, কিন্তু clipboard history থেকে যেতে পারে।

Quotas → Quick Update → Save changes। পরেরবার একই HTTPS URL খুললে edited percentage থাকার কথা; physical Android Chrome-এ আলাদা acceptance test প্রয়োজন। প্রতিবার নতুন HTML download লাগবে না।

সাবধান: localStorage encrypted নয় এবং cloud sync-ও নয়। Site data clear হলে data হারাতে পারে; নিয়মিত private JSON backup আলাদা জায়গায় রাখুন। Grok-এর 5-hour pool অনুমান করে ঢোকাবেন না।