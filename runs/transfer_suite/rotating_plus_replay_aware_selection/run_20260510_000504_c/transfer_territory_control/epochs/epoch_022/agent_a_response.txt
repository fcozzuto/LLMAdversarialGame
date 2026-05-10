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

    def best_neighbor_towards(tx, ty):
        best = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h):
                continue
            # Deterministic preference: closer to target, and avoid obstacles when possible
            dist = max(abs(nx - tx), abs(ny - ty))
            pen_obs = 0 if (nx, ny) not in obstacles else 2
            # Prefer moving off-board? already excluded.
            key = (dist + pen_obs, abs(nx - sx) + abs(ny - sy), dy, dx)
            if best is None or key < best[0]:
                best = (key, dx, dy)
        return [best[1], best[2]] if best else [0, 0]

    # Frontier targets: unclaimed adjacent to our territory
    if self_terr and unclaimed:
        frontier = []
        for cx, cy in unclaimed:
            if ((cx - 1, cy) in self_terr or (cx + 1, cy) in self_terr or
                (cx, cy - 1) in self_terr or (cx, cy + 1) in self_terr):
                frontier.append((cx, cy))
    else:
        frontier = []

    # Score frontier cells: closer to us (reachable) and closer to opponent (stronger swing)
    if frontier:
        opp_list = list(opp_terr) if opp_terr else [(ox, oy)]
        best_t = None
        best_key = None
        for cx, cy in frontier:
            if (cx, cy) in obstacles:
                continue
            d_us = abs(cx - sx) + abs(cy - sy)
            d_opp = min(abs(cx - px) + abs(cy - py) for px, py in opp_list)
            # Small bias to push toward opponent corner-ish (based on opponent position)
            bias = abs(cx - ox) + abs(cy - oy)
            # Lower is better
            key = (d_opp, d_us, bias, cy, cx)
            if best_key is None or key < best_key:
                best_key = key
                best_t = (cx, cy)
        if best_t:
            tx, ty = best_t
            return best_neighbor_towards(tx, ty)

    # If no frontier, grab nearest unclaimed, else press toward opponent territory
    targets = list(unclaimed)
    if targets:
        # Tie-break deterministically
        tx, ty = min(targets, key=lambda p: (abs(p[0] - sx) + abs(p[1] - sy), p[1], p[0]))
        return best_neighbor_towards(tx, ty)

    if opp_terr:
        tx, ty = min(list(opp_terr), key=lambda p: (abs(p[0] - sx) + abs(p[1] - sy), p[1], p[0]))
        return best_neighbor_towards(tx, ty)

    # Last resort: move toward opponent position (diagonal allowed), avoid obstacles if possible
    tx, ty = ox, oy
    return best_neighbor_towards(tx, ty)