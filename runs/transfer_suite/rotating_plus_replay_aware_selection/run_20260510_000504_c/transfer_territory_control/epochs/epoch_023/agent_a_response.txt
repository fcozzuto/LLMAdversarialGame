def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))
    self_terr = set(map(tuple, observation.get("self_territory") or []))
    opp_terr = set(map(tuple, observation.get("opponent_territory") or []))
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def step_towards(tx, ty, prefer_opp_enter=False):
        best = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            pen = 0
            if (nx, ny) in obstacles:
                pen += 10
            if (nx, ny) in opp_terr:
                pen += 0 if prefer_opp_enter else 1
            # Prefer lower chebyshev distance, then lower movement, then deterministic tie-break
            dist = max(abs(nx - tx), abs(ny - ty))
            key = (dist + pen, abs(nx - sx) + abs(ny - sy), dx, dy)
            if best is None or key < best[0]:
                best = (key, dx, dy)
        return [best[1], best[2]] if best else [0, 0]

    # Prefer capturing adjacent unclaimed from our territory
    if self_terr and unclaimed:
        frontier = []
        for x, y in self_terr:
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if (nx, ny) in unclaimed and inb(nx, ny):
                    # Favor targets that are farther from obstacles and also closer to opponent side
                    obs_adj = 0
                    for ddx, ddy in dirs:
                        ax, ay = nx + ddx, ny + ddy
                        if inb(ax, ay) and (ax, ay) in obstacles:
                            obs_adj += 1
                    frontier.append((nx, ny, obs_adj))
        if frontier:
            # Deterministic: minimize our distance + penalize obstacle adjacency + pull toward opponent
            target = min(frontier, key=lambda t: (max(abs(t[0] - sx), abs(t[1] - sy)) + 2 * t[2] - 0.15 * (abs(ox - t[0]) + abs(oy - t[1])), t[0], t[1]))
            return step_towards(target[0], target[1], prefer_opp_enter=False)

    # If no frontier, either take any unclaimed near the center or pressure opponent territory
    targets = list(unclaimed) if unclaimed else []
    if not targets:
        # Go toward opponent to enable deterministic counterclaim pressure
        return step_towards(ox, oy, prefer_opp_enter=True)

    cx, cy = (w - 1) // 2, (h - 1) // 2
    # If our territory exists, bias away from stagnation by going toward unclaimed closest to opponent side
    prefer_to_opp = bool(self_terr)
    if prefer_to_opp:
        target = min(targets, key=lambda t: (max(abs(t[0] - sx), abs(t[1] - sy)) - 0.25 * (abs(ox - t[0]) + abs(oy - t[1])), abs(t[0] - cx) + abs(t[1] - cy), t[0], t[1]))
    else:
        target = min(targets, key=lambda t: (max(abs(t[0] - sx), abs(t[1] - sy)) + 0.05 * (abs(t[0] - cx) + abs(t[1] - cy)), t[0], t[1]))
    return step_towards(target[0], target[1], prefer_opp_enter=False)