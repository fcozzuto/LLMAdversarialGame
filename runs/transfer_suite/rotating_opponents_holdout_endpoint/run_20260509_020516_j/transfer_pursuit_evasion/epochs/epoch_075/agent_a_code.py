def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    obstacles = set()
    for it in (observation.get("obstacles") or []):
        try:
            if isinstance(it, dict):
                x, y = it.get("x"), it.get("y")
            else:
                x, y = it[0], it[1]
            x, y = int(x), int(y)
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
        except Exception:
            pass

    self_role = (observation.get("self_role") or "").lower()
    opp_role = (observation.get("opponent_role") or "").lower()
    evader = ("evader" in self_role) and ("evader" not in opp_role)
    pursuer = not evader

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    turn = int(observation.get("turn_index", 0))

    # Evader: deterministic zigzag away, alternating preferred axis by parity.
    # Pursuer: deterministic greedy pursuit with obstacle-aware tie-break (prefer diagonal/higher clearance).
    best = None
    best_sc = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue

        man = abs(nx - ox) + abs(ny - oy)
        dxo, dyo = nx - ox, ny - oy
        d2 = dxo * dxo + dyo * dyo

        # Clearance: count available neighbor squares to reduce getting stuck.
        neigh = 0
        for ddx, ddy in moves:
            tx, ty = nx + ddx, ny + ddy
            if inside(tx, ty):
                neigh += 1

        if evader:
            # Alternate between maximizing x-distance and y-distance to counter zigzag.
            parity = (turn & 1)
            fx = abs(nx - ox)
            fy = abs(ny - oy)
            corner_pref = (nx + ny) if (ox + oy) < (w - 1 + h - 1) else ((w - 1 - nx) + (h - 1 - ny))
            score = (man * 10.0) + (fx if parity else fy) + neigh * 0.8 + corner_pref * 0.01
            # Small penalty for moving directly onto the pursuer line to avoid easy capture trajectories.
            if (ox == nx) or (oy == ny):
                score -= 1.5
        else:
            # Pursuer: reduce distance primarily; second prefer diagonals and higher clearance.
            diag = 1.0 if (dx != 0 and dy != 0) else 0.0
            score = (-man * 10.0) + d2 * (-0.02) + neigh * 0.9 + diag * 0.6
            # If movement doesn't improve manhattan, add a slight turn-based bias to avoid oscillation.
            if man >= abs(sx - ox) + abs(sy - oy):
                score -= 0.2 if ((turn + nx + ny) & 1) == 0 else 0.0

        # Deterministic tie-break: lowest resulting (x,y) hash-like.
        if best_sc is None or score > best_sc or (score == best_sc and (nx, ny) < (best[0], best[1])):
            best_sc = score
            best = (nx, ny, dx, dy)

    return [int(best[2]), int(best[3])] if best is not None else [0, 0]