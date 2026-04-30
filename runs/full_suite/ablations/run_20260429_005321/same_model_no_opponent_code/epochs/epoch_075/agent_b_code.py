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
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    def adj_obst_pen(x, y):
        p = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if (nx, ny) in obstacles:
                    p += 1
        return p

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    best = (None, -10**18)

    # If no resources, go to a point that maximizes distance from opponent while staying safe.
    if not resources:
        tx, ty = w // 2, h // 2
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            score = dist2(nx, ny, ox, oy) - 0.25 * dist2(nx, ny, tx, ty) - 0.6 * adj_obst_pen(nx, ny)
            if score > best[1]:
                best = ((dx, dy), score)
        return [best[0][0], best[0][1]] if best[0] is not None else [0, 0]

    # Resource-choice that favors ones we can reach sooner than the opponent.
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        # Slight bias toward staying consistent (reduces oscillation) and toward blocking via obstacle adjacency.
        base = -0.15 * dist2(nx, ny, sx, sy) - 0.7 * adj_obst_pen(nx, ny) - 0.05 * dist2(nx, ny, ox, oy)
        best_res = -10**18
        for rx, ry in resources:
            ds = dist2(nx, ny, rx, ry)
            do = dist2(ox, oy, rx, ry)
            # Higher is better: smaller ds; larger (do-ds) means we are ahead relative to opponent.
            val = -ds + 0.9 * (do - ds)
            # Encourage grabbing if adjacent/in place.
            if ds == 0:
                val += 10_000
            elif ds <= 2:
                val += 80
            if val > best_res:
                best_res = val
        score = base + best_res
        # Deterministic tie-break: prefer smaller |dx|+|dy| then lexicographically.
        if score > best[1]:
            best = ((dx, dy), score)
        elif score == best[1] and best[0] is not None:
            cur = abs(dx) + abs(dy)
            prev = abs(best[0][0]) + abs(best[0][1])
            if cur < prev or (cur == prev and (dx, dy) < best[0]):
                best = ((dx, dy), score)

    if best[0] is None:
        return [0, 0]
    return [best[0][0], best[0][1]]