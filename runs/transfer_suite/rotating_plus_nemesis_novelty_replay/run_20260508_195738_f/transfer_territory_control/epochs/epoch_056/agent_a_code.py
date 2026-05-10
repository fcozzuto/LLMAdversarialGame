def choose_move(observation):
    x, y = observation.get("self_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    obstacles = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles)
    opp = set((p[0], p[1]) for p in (observation.get("opponent_territory", []) or []))
    unclaimed = set((p[0], p[1]) for p in (observation.get("unclaimed_cells", []) or []))
    selft = set((p[0], p[1]) for p in (observation.get("self_territory", []) or []))
    opp_pos = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    ox, oy = opp_pos[0], opp_pos[1]

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def adj8(nx, ny):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                ax, ay = nx + dx, ny + dy
                if inb(ax, ay):
                    yield ax, ay

    def md_to_set(nx, ny, s):
        if not s:
            return 10**9
        m = 10**9
        for px, py in s:
            d = abs(px - nx) + abs(py - ny)
            if d < m:
                m = d
        return m

    best = None
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        if (nx, ny) in opp:
            base = 14.0
        elif (nx, ny) in unclaimed:
            base = 7.0
        elif (nx, ny) in selft:
            base = 1.0
        else:
            base = 0.5

        front = 0.0
        near_opp = 0.0
        near_self = 0.0
        for ax, ay in adj8(nx, ny):
            if (ax, ay) in opp:
                near_opp += 1.0
            if (ax, ay) in selft:
                near_self += 1.0
        if base < 7.0 and (nx, ny) not in selft and near_self > 0:
            front += 2.0
        if (nx, ny) not in opp and near_opp > 0:
            front -= 2.2 * near_opp
        if (nx, ny) in opp:
            front += 0.4 * near_opp  # more adjacent opponent territory => better flip path

        dist_to_opp = abs(ox - nx) + abs(oy - ny)
        opp_gap = -0.12 * dist_to_opp  # stay away while expanding
        reach_to_unclaimed = 0.0
        if unclaimed:
            reach_to_unclaimed = 0.18 * (6 - min(md_to_set(nx, ny, unclaimed), 6))

        score = base + front + opp_gap + reach_to_unclaimed
        if best is None or score > best_score or (score == best_score and (dx, dy) < best):
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]