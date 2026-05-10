def choose_move(observation):
    x, y = observation.get("self_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    obs_cells = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))
    opp_terr = set((p[0], p[1]) for p in (observation.get("opponent_territory", []) or []))
    self_terr = set((p[0], p[1]) for p in (observation.get("self_territory", []) or []))
    unclaimed = set((p[0], p[1]) for p in (observation.get("unclaimed_cells", []) or []))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    opp_cx = opp_cy = None
    if opp_terr:
        s = 0
        sx = sy = 0
        for px, py in opp_terr:
            sx += px
            sy += py
            s += 1
        opp_cx = sx / s
        opp_cy = sy / s
    else:
        opp_cx, opp_cy = w - 1 - x, h - 1 - y

    def score_cell(cx, cy):
        if (cx, cy) in obs_cells:
            return -10**9
        s = 0.0
        if (cx, cy) in self_terr:
            s += 0.2
        elif (cx, cy) in opp_terr:
            s += 3.5
        elif (cx, cy) in unclaimed:
            s += 2.2
        # Prefer pushing away from opponent center to control space
        d_opp = abs(cx - opp_cx) + abs(cy - opp_cy)
        s += 0.015 * d_opp
        # Prefer closer to any frontier (unclaimed adjacent to self, or near opponent)
        frontier = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = cx + dx, cy + dy
                if not inb(nx, ny):
                    continue
                if (nx, ny) in unclaimed:
                    frontier += 1
                elif (nx, ny) in opp_terr:
                    frontier += 0.5
        s += 0.6 * frontier
        return s

    best = (-10**18, 0, 0)
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or (nx, ny) in obs_cells:
            continue
        s = score_cell(nx, ny)

        # Small tie-break: stay still if equally good early to reduce flip-risk
        if dx == 0 and dy == 0 and s > best[0] - 1e-9:
            s += 0.05
        if s > best[0] + 1e-9:
            best = (s, dx, dy)

    # If all moves were invalid (shouldn't happen), stay put
    if best[0] < -1e8:
        return [0, 0]
    return [int(best[1]), int(best[2])]