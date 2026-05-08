def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles") or []
    blocked = set()
    for p in obstacles:
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))
        except:
            pass

    self_t = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []))
    opp_t = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))
    unclaimed = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or []))

    # Prefer captures and contesting near opponent; also drift toward the map center.
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    opp_list = list(opp_t) if opp_t else []
    def dist_to_nearest(px, py, s):
        if not s:
            return 10**9
        md = 10**9
        for x, y in s:
            d = abs(x - px) + abs(y - py)
            if d < md:
                md = d
        return md

    my_to_opp = dist_to_nearest(sx, sy, opp_t)

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    move_order = sorted(dirs, key=lambda d: (abs(d[0]) + abs(d[1]), d[0], d[1]))

    best = None
    best_score = -10**18

    for dx, dy in move_order:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in blocked:
            continue

        score = 0.0
        if (nx, ny) in opp_t:
            score += 20.0  # flipping opponent territory on entry
        elif (nx, ny) in unclaimed:
            score += 6.0
        elif (nx, ny) in self_t:
            score += 2.0
        else:
            score += 0.5

        dopp = dist_to_nearest(nx, ny, opp_t)
        # Move to reduce distance to opponent territory once we have some proximity.
        if my_to_opp < 10**8 and opp_list:
            score += (my_to_opp - dopp) * 2.2

        # Control the center slightly to avoid stalling in corners.
        score += -0.25 * (abs(nx - cx) + abs(ny - cy))

        # Mild preference for not stepping away from any currently own territory boundary.
        if self_t:
            score += -0.05 * dist_to_nearest(nx, ny, self_t)

        # Deterministic tie-breaking
        if score > best_score:
            best_score = score
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best