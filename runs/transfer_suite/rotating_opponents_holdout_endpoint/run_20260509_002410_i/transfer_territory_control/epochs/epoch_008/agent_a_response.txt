def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))

    def inside(x, y): return 0 <= x < w and 0 <= y < h

    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_t = set(map(tuple, observation.get("self_territory") or []))
    opp_t = set(map(tuple, observation.get("opponent_territory") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))

    if not unclaimed and not (self_t or opp_t):
        return [0, 0]

    neigh = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cand = []

    for dx, dy in neigh:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue

        d_opp = abs(nx - ox) + abs(ny - oy)
        d_self = abs(nx - sx) + abs(ny - sy)
        d_enemy = d_opp

        in_opp = (nx, ny) in opp_t
        in_self = (nx, ny) in self_t
        is_unclaimed = (nx, ny) in unclaimed

        if unclaimed:
            d_un = min(abs(nx - ux) + abs(ny - uy) for ux, uy in unclaimed)
        else:
            cx, cy = w // 2, h // 2
            d_un = abs(nx - cx) + abs(ny - cy)

        # Greedy expansion while pressuring opponent boundary; deterministic tie-break via score then move order.
        score = 0
        if is_unclaimed:
            score += 6
        if in_opp:
            score += 8  # flipping into opponent territory is valuable
        if in_self:
            score -= 1  # prefer claiming/stealing rather than re-entering own cells

        score += (12 - d_un) * 0.7
        score += (7 - d_enemy) * 0.35 if in_opp else (3 - d_enemy) * 0.15
        score -= d_self * 0.05

        # If directly adjacent to opponent, prioritize capturing their adjacent cells if possible.
        if max(abs(nx - ox), abs(ny - oy)) == 1 and in_opp:
            score += 4

        cand.append((score, dx, dy))

    if not cand:
        return [0, 0]
    cand.sort(key=lambda t: (-t[0], neigh.index((t[1], t[2])) if (t[1], t[2]) in neigh else 99))
    _, dx, dy = cand[0]
    return [int(dx), int(dy)]