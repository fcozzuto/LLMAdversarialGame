def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw = int(observation.get("grid_width", 8))
    gh = int(observation.get("grid_height", 8))

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            px, py = int(p[0]), int(p[1])
            if 0 <= px < gw and 0 <= py < gh:
                obs.add((px, py))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < gw and 0 <= ry < gh and (rx, ry) not in obs:
                resources.append((rx, ry))
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # "Interception" heuristic: prefer resources where we are closer than opponent;
    # otherwise, still pick something that minimizes opponent's advantage.
    def best_target_after(nx, ny):
        best = None
        best_val = -10**18
        for rx, ry in resources:
            self_d = abs(rx - nx) + abs(ry - ny)
            opp_d = abs(rx - ox) + abs(ry - oy)
            val = (opp_d - self_d) * 10 - self_d
            if best is None or val > best_val or (val == best_val and self_d < best[0]):
                best_val = val
                best = (self_d, rx, ry, opp_d)
        return best_val

    best_move = (0, 0)
    best_val = -10**18
    # Deterministic tie-break: prefer moves with greater progress toward chosen target,
    # then prefer fewer steps (non-stay), then lexicographic.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < gw and 0 <= ny < gh):
            continue
        if (nx, ny) in obs:
            continue
        val = best_target_after(nx, ny)
        # discourage staying if not required
        if dx == 0 and dy == 0:
            val -= 0.5
        if val > best_val:
            best_val = val
            best_move = (dx, dy)
        elif val == best_val:
            if (dx, dy) != (0, 0) and best_move == (0, 0):
                best_move = (dx, dy)
            elif (dx, dy) != (0, 0) and best_move != (0, 0):
                if (dx, dy) < best_move:
                    best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]