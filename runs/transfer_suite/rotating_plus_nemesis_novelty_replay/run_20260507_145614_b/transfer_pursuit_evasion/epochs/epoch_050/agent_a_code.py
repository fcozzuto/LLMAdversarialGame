def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    self_role = observation.get("self_role", "pursuer") or "pursuer"

    obst = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((int(p[0]), int(p[1])))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    def mob_count(x, y):
        c = 0
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if inb(nx, ny):
                c += 1
        return c

    # target half-corners selection to encourage trapping/cutoffs deterministically
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    # choose corner farthest from opponent for pursuer cutoff, opposite for evader
    corner_far = max(corners, key=lambda c: dist2(ox, oy, c[0], c[1]))
    corner_near = min(corners, key=lambda c: dist2(ox, oy, c[0], c[1]))

    best = (0, 0)
    best_val = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        if self_role.lower() == "evader":
            d = dist2(nx, ny, ox, oy)
            # avoid crowding pursuer and reduce own mobility loss near tight spots
            m_self = mob_count(nx, ny)
            m_purs = mob_count(ox, oy)
            # if pursuer can force near, bias toward opposite corner
            dc = dist2(nx, ny, corner_far[0], corner_far[1])
            # higher is better for evader
            val = (d * 1.0) + (dc * 0.02) + (m_self * 0.1) - (m_purs * 0.02)
            if best_val is None or val > best_val:
                best_val = val
                best = (dx, dy)
        else:
            d = dist2(nx, ny, ox, oy)
            # minimize opponent mobility after move; stronger when opponent is adjacent to obstacles
            m_opp = mob_count(ox, oy)
            dc = dist2(nx, ny, corner_near[0], corner_near[1])
            # also discourage moving away from the opponent's "near corner"
            val = (d * 1.0) - (m_opp * 0.35) + (dc * 0.01)
            if best_val is None or val < best_val:
                best_val = val
                best = (dx, dy)

    return [int(best[0]), int(best[1])]