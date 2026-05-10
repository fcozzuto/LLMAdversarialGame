def choose_move(observation):
    sx, sy = observation["self_position"]
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    obstacles = set(map(tuple, observation.get("obstacles", [])))
    self_t = set(map(tuple, observation.get("self_territory", [])))
    opp_t = set(map(tuple, observation.get("opponent_territory", [])))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells", [])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def neigh8(x, y):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx != 0 or dy != 0:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < w and 0 <= ny < h:
                        yield nx, ny

    # Target selection (deterministic)
    center = (w // 2 - 1, h // 2 - 1)  # (3,3) on 8x8
    candidates = []
    if unclaimed:
        for x, y in unclaimed:
            adj_opp = any((nx, ny) in opp_t for nx, ny in neigh8(x, y))
            adj_self = any((nx, ny) in self_t for nx, ny in neigh8(x, y))
            if adj_opp:
                candidates.append((2, abs(x - center[0]) + abs(y - center[1]), x, y))
            elif adj_self:
                candidates.append((1, abs(x - center[0]) + abs(y - center[1]), x, y))
    if candidates:
        candidates.sort()
        _, _, tx, ty = candidates[0]
    else:
        if self_t:
            # If we already own something, push to nearest unclaimed to our front; else to center
            best = None
            for x, y in unclaimed or [center]:
                d = min(abs(x - ax) + abs(y - ay) for ax, ay in self_t) if unclaimed else 0
                val = (d, x, y)
                if best is None or val < best[0]:
                    best = (val, (x, y))
            tx, ty = best[1]
        else:
            tx, ty = center

    # Evaluate next moves (stay allowed)
    best_move = [0, 0]
    best_val = None
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            if (nx, ny) in obstacles:
                continue

            if (nx, ny) in opp_t:
                wgt = 8
            elif (nx, ny) in self_t:
                wgt = 1
            elif (nx, ny) in unclaimed:
                # Prefer stepping into contested spots near opponent; otherwise closer to target
                adj_opp = any((ax, ay) in opp_t for ax, ay in neigh8(nx, ny))
                adj_self = any((ax, ay) in self_t for ax, ay in neigh8(nx, ny))
                wgt = 4 if adj_opp else (3 if adj_self else 2)
            else:
                wgt = 0

            # Deterministic tie-breaker favors closer to target then toward upper-left
            val = (-(wgt * 10) + (abs(nx - tx) + abs(ny - ty)) * 3, ny, nx)
            if best_val is None or val < best_val:
                best_val = val
                best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]