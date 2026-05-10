def choose_move(observation):
    w = int(observation.get("grid_width", 8)); h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    inb = lambda x, y: 0 <= x < w and 0 <= y < h
    def blocked(x, y): return (x, y) in obstacles

    selfT = set(tuple(p) for p in (observation.get("self_territory") or []))
    oppT = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    uncla = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    turn = int(observation.get("turn_index", 0))

    # Pick the best among legal immediate moves using a simple deterministic scoring heuristic.
    best = None
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                nx, ny = sx, sy
            else:
                nx, ny = sx + dx, sy + dy
                if not inb(nx, ny) or blocked(nx, ny):
                    continue

            if (nx, ny) in selfT:
                val = 0.2
            elif (nx, ny) in uncla:
                val = 2.2
            elif (nx, ny) in oppT:
                val = 3.4  # likely to flip on entry
            else:
                val = 1.1  # unknown cell; treat as expandable

            # Encourage toward useful frontier and away from opponent proximity is not always best; slight centering.
            dist_center = abs(nx - cx) + abs(ny - cy)
            dist_opp = abs(nx - ox) + abs(ny - oy)

            # Bias: expand while keeping some distance from opponent to avoid being boxed.
            val += -0.06 * dist_center + 0.01 * (dist_opp)

            # Deterministic tie-breaker from turn parity and move direction.
            val += (dx * 0.001 - dy * 0.0007) + (1 if ((dx + 2 * dy + turn) & 1) == 0 else 0)

            if best is None or val > best[0]:
                best = (val, dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[1]), int(best[2])]