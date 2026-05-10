def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or sp
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    self_ter = set((int(p[0]), int(p[1])) for p in (observation.get("self_territory") or []) if isinstance(p, (list, tuple)) and len(p) >= 2)
    opp_ter = set((int(p[0]), int(p[1])) for p in (observation.get("opponent_territory") or []) if isinstance(p, (list, tuple)) and len(p) >= 2)
    unclaimed = [(int(p[0]), int(p[1])) for p in (observation.get("unclaimed_cells") or []) if isinstance(p, (list, tuple)) and len(p) >= 2]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def neigh8(x, y):
        return [(x+dx, y+dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if not (dx == 0 and dy == 0) and inb(x+dx, y+dy)]

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    opp_count = int(observation.get("opponent_territory_count") or len(opp_ter))
    self_count = int(observation.get("self_territory_count") or len(self_ter))
    target_list = unclaimed

    # If we're behind, contest near opponent frontier; else expand toward center/open space.
    behind = self_count <= opp_count
    best = None
    best_score = None

    for tx, ty in target_list:
        if (tx, ty) in self_ter or (tx, ty) in opp_ter:
            continue
        if (tx, ty) in obstacles:
            continue

        is_adj_to_opp = 0
        if behind:
            for nx, ny in neigh8(tx, ty):
                if (nx, ny) in opp_ter:
                    is_adj_to_opp = 1
                    break

        # Penalize "tight" cells (many obstacles around) to avoid getting stuck.
        obs_near = 0
        for nx, ny in neigh8(tx, ty):
            if (nx, ny) in obstacles:
                obs_near += 1

        # Deterministic movement: greedy toward target, but score considers center and frontier.
        d = abs(tx - sx) + abs(ty - sy)
        center_d = abs(tx - cx) + abs(ty - cy)

        if behind:
            # Strongly prefer cells adjacent to opponent territory.
            score = (0 if is_adj_to_opp else 1000) + 2 * d + 3 * obs_near + 0.2 * center_d
        else:
            # Prefer closer to center; avoid obstacle traps; also mildly prefer outward expansion.
            score = d + 0.8 * center_d + 2.5 * obs_near

        if best_score is None or score < best_score or (score == best_score and (tx, ty) < best):
            best_score = score
            best = (tx, ty)

    if best is None:
        return [0, 0]

    tx, ty = best
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    # Avoid stepping into a known obstacle if possible (stay or alternate axis).
    nx, ny = sx + dx, sy + dy
    if (nx, ny) in obstacles:
        if (sx + dx, sy) not in obstacles:
            return [dx, 0]
        if (sx, sy + dy) not in obstacles:
            return [0, dy]
        return [0, 0]
    return [dx, dy]