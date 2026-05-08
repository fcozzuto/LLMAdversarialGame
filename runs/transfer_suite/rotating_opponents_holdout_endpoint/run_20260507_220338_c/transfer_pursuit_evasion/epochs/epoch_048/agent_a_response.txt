def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            bx, by = int(p[0]), int(p[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    role_s = str(observation.get("self_role") or "").lower()
    is_evader = any(k in role_s for k in ("evad", "run", "away", "escape", "runner"))
    is_pursuer = ("purs" in role_s) or ("hunt" in role_s) or ("chase" in role_s)
    if not (is_evader or is_pursuer):
        # If role unknown, default to evasion when closer to opponent than to corner
        is_evader = True

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist_to_opp_cheb(x, y):
        dx = abs(ox - x)
        dy = abs(oy - y)
        return dx if dx > dy else dy

    obs_list = list(blocked)

    def min_obs_manh(x, y):
        if not obs_list:
            return 99
        best = 99
        for bx, by in obs_list:
            d = abs(bx - x) + abs(by - y)
            if d < best:
                best = d
        return best

    best = None
    best_score = None

    for dx, dy in moves:
        x, y = sx + dx, sy + dy
        if not inb(x, y):
            continue
        if (x, y) in blocked:
            continue

        dopp = dist_to_opp_cheb(x, y)
        dobs = min_obs_manh(x, y)

        # Heuristic weights: avoid obstacles and (as pursuer) decrease distance sharply; as evader, increase distance.
        if is_evader:
            score = (dopp * 100) + (dobs * 2)
        else:
            # Prefer moving closer; also avoid getting blocked.
            score = (-dopp * 100) + (dobs * 1) - (abs(x - ox) + abs(y - oy))

        if best is None or score > best_score:
            best_score = score
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]