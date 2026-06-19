import { AccountFooter } from "@/features/profile/components/account-footer";
import { BookmarkedFightersGrid } from "@/features/profile/components/bookmarked-fighters-grid";
import { NotificationPreferences } from "@/features/profile/components/notification-preferences";
import { SetPasswordBanner } from "@/features/profile/components/set-password-banner";

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
