def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    opp_t = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    un_t = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))
    obs = set(tuple(p) for p in (observation.get("obstacles") or []))

    options = [(-1, -1), (-1, 0), (-1, 1),
               (0, -1), (0, 0), (0, 1),
               (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def md(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx + dy

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    ox, oy = observation["opponent_position"]

    my_t = set(tuple(p) for p in (observation.get("self_territory") or []))
    best = [0, 0]
    best_s = -10**18

    # Pick a compact set of strategic targets deterministically
    un_list = list(un_t)
    # Prefer cells near center-frontier; if none, use any unclaimed; if none, fallback.
    frontier = []
    for x, y in un_list:
        dmid = abs(x - cx) + abs(y - cy)
        dopp = md(x, y, ox, oy)
        frontier.append((dmid - 0.3 * dopp, dmid, dopp, x, y))
    frontier.sort(key=lambda t: (t[0], t[1], -t[2], t[3], t[4]))
    targets = []
    for t in frontier[:10]:
        targets.append((t[3], t[4]))
    if not targets:
        for x, y in un_list[:10]:
            targets.append((x, y))

    # Evaluate immediate moves
    for dx, dy in options:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        s = 0
        if (nx, ny) in opp_t:
            s += 5000
        if (nx, ny) in un_t:
            s += 1200
        # keep momentum into useful territory
        if (nx, ny) in my_t:
            s += 30

        # Aim toward best nearby target; if none, toward center but away from opponent
        if targets:
            best_td = 10**9
            for tx, ty in targets[:6]:
                d = md(nx, ny, tx, ty)
                if d < best_td:
                    best_td = d
            s += 800 - 120 * best_td
        s += -40 * (abs(nx - cx) + abs(ny - cy))
        s += 0.2 * md(nx, ny, ox, oy)  # don't get too close to sweeper

        if s > best_s or (s == best_s and (dx, dy) < (best[0], best[1])):
            best_s = s
            best = [dx, dy]

    if best_s <= -10**17:
        return [0, 0]
    return best