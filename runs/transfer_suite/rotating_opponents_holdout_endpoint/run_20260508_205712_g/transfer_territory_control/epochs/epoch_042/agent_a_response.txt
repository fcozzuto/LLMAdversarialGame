def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    ox, oy = observation.get("opponent_position") or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    self_terr = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_terr = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))

    neigh8 = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    candidates = []
    for dx, dy in neigh8:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            candidates.append((dx, dy, nx, ny))

    opp_adj = set()
    for (x, y) in self_terr:
        for dx, dy in [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                if (nx, ny) in opp_terr:
                    opp_adj.add((nx, ny))

    targets = []
    for p in opp_adj:
        targets.append(p)
    for p in unclaimed:
        targets.append(p)
    targets_list = targets if targets else list(unclaimed)[:64]

    def dist2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    best_dxdy = (0, 0)
    best_val = -10**18
    tcount = len(targets_list)

    for dx, dy, nx, ny in candidates:
        val = 0.0
        if (nx, ny) in opp_terr:
            val += 2500.0
        if (nx, ny) in unclaimed:
            val += 1200.0
        if (nx, ny) in self_terr:
            val += 10.0
        if (nx, ny) in unclaimed or (nx, ny) in opp_terr:
            if tcount:
                bestd = None
                for tx, ty in targets_list:
                    d = dist2(nx, ny, tx, ty)
                    if bestd is None or d < bestd:
                        bestd = d
                val += 500.0 / (1.0 + bestd)
            val += 0.01 * (dist2(ox, oy, sx, sy) - dist2(ox, oy, nx, ny))
        else:
            val -= 20.0

        # deterministic tie-break: prefer lexicographically smaller (dx,dy) after value
        if val > best_val + 1e-9 or (abs(val - best_val) <= 1e-9 and (dx, dy) < best_dxdy):
            best_val = val
            best_dxdy = (dx, dy)

    return [int(best_dxdy[0]), int(best_dxdy[1])]