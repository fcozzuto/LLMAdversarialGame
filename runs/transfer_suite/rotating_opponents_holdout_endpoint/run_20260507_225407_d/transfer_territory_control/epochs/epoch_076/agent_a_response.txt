def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    self_terr = set(tuple(t) for t in (observation.get("self_territory") or []))
    opp_terr = set(tuple(t) for t in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(t) for t in (observation.get("unclaimed_cells") or []))
    resources = [tuple(t) for t in (observation.get("resources") or [])]

    def blocked(x, y):
        return not (0 <= x < w and 0 <= y < h) or (x, y) in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    neighbors_opp = set()
    for (x, y) in opp_terr:
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                neighbors_opp.add((nx, ny))

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    best = [0, 0]
    best_val = None

    # Preference targets: resources -> unclaimed adjacent to opp -> other unclaimed -> center
    if resources:
        targets = resources
    else:
        targets = [p for p in unclaimed if p in neighbors_opp]
        if not targets:
            targets = list(unclaimed)
        if not targets:
            targets = [(w // 2, h // 2)]

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            val = -10**9
        else:
            val = 0.0
            if (nx, ny) in opp_terr:
                val += 8.0  # flipping immediate
            if (nx, ny) in unclaimed:
                val += 4.0
            if (nx, ny) in self_terr:
                val -= 1.0  # avoid stagnating
            # push toward best target with slight repulsion from opponent to avoid edge races
            dmin = 10**9
            for tx, ty in targets:
                d = man(nx, ny, tx, ty)
                if d < dmin:
                    dmin = d
            val += -0.7 * dmin
            val += 0.15 * man(nx, ny, ox, oy)
            # if opponent is near, bias toward their immediate frontier
            if neighbors_opp:
                df = man(nx, ny, ox, oy)
                # reward being closer to any frontier cell
                frontier_d = 10**9
                for fx, fy in neighbors_opp:
                    d = man(nx, ny, fx, fy)
                    if d < frontier_d:
                        frontier_d = d
                val += 0.3 * max(0, 4 - frontier_d) - 0.05 * df

        if best_val is None or val > best_val or (val == best_val and (dx, dy) == (best[0], best[1])):
            best_val = val
            best = [dx, dy]

    return [int(best[0]), int(best[1])]