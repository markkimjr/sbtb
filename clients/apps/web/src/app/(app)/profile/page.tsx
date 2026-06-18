import { AccountFooter } from "@/components/profile/account-footer";
import { BookmarkedFightersGrid } from "@/components/profile/bookmarked-fighters-grid";
import { NotificationPreferences } from "@/components/profile/notification-preferences";
import { SetPasswordBanner } from "@/components/profile/set-password-banner";

export default function ProfilePage() {
  return (
    <div className="max-w-2xl mx-auto px-6 py-10 space-y-10 w-full">
      <h1 className="font-display italic text-4xl">Profile</h1>
      <SetPasswordBanner />
      <NotificationPreferences />
      <BookmarkedFightersGrid />
      <AccountFooter />
    </div>
  );
}
