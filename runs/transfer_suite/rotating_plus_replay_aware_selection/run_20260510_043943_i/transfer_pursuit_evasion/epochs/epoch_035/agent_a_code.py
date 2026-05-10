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
            obstacles.add((int(p[0]), int(p[1])))

    role_self = (observation.get("self_role") or "").lower()
    evader = ("evader" in role_self) or ("pursuer" not in role_self and "hunter" not in role_self and "chaser" not in role_self)

    moves = (-1, 0, 1)
    best = None
    best_score = None
    for dx in moves:
        for dy in moves:
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h):
                continue
            if (nx, ny) in obstacles:
                continue
            ddx, ddy = nx - ox, ny - oy
            dist2 = ddx * ddx + ddy * ddy

            # Move-like potential to reduce zigzag predictability: bias against staying on same parity line when evading,
            # and bias toward closing lines when pursuing.
            parity = (nx + ny) & 1
            cur_parity = (sx + sy) & 1

            # Soft obstacle-aware term: prefer moves with fewer blocked adjacent cells.
            blocked_adj = 0
            for ax in (-1, 0, 1):
                for ay in (-1, 0, 1):
                    if ax == 0 and ay == 0:
                        continue
                    tx, ty = nx + ax, ny + ay
                    if 0 <= tx < w and 0 <= ty < h and (tx, ty) in obstacles:
                        blocked_adj += 1

            # Also try to keep away from board edges when evading; and toward edges when pursuing (deterministic).
            edge_dist = min(nx, ny, w - 1 - nx, h - 1 - ny)

            if evader:
                score = dist2
                score += 0.05 * edge_dist
                score += 0.2 * (cur_parity != parity)  # alternate parity helps against zigzag
                score -= 0.1 * blocked_adj
            else:
                score = -dist2
                score -= 0.03 * edge_dist
                score += 0.05 * (cur_parity != parity)  # helps avoid simple oscillations
                score -= 0.08 * blocked_adj

            if best is None or (score > best_score):
                best_score = score
                best = [dx, dy]

    if best is None:
        return [0, 0]
    return best