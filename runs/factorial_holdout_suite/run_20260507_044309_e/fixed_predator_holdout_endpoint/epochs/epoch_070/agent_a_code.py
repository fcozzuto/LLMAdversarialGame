def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            px, py = int(p[0]), int(p[1])
            if 0 <= px < w and 0 <= py < h:
                obstacles.add((px, py))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))
    if not resources:
        return [0, 0]

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = (-10**9, None)

    # Greedy contest: pick the move that maximizes your lead over the opponent on the best remaining resource.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue

        # For each resource, compute "advantage": (opp_distance - self_distance).
        # Prefer larger advantage; if tied, prefer smaller self distance.
        local_best = (-10**9, 10**9)
        for rx, ry in resources:
            self_d = man(nx, ny, rx, ry)
            opp_d = man(ox, oy, rx, ry)
            adv = opp_d - self_d
            cand = (adv, self_d)
            if cand[0] > local_best[0] or (cand[0] == local_best[0] and cand[1] < local_best[1]):
                local_best = cand

        if local_best[0] > best[0] or (local_best[0] == best[0] and local_best[1] < (best[1] or (0, 0))[1]):
            best = (local_best[0], (dx, dy, local_best[1]))
        elif local_best[0] == best[0] and isinstance(best[1], tuple) and local_best[0] != -10**9:
            # Secondary tie-break for determinism: closer self, then lexicographic move.
            cur = best[1]
            if local_best[1] < cur[2] or (local_best[1] == cur[2] and (dx, dy) < (cur[0], cur[1])):
                best = (local_best[0], (dx, dy, local_best[1]))

    if best[1] is None:
        return [0, 0]
    return [int(best[1][0]), int(best[1][1])]