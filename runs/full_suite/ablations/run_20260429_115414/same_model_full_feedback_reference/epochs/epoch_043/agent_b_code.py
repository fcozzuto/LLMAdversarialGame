def choose_move(observation):
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [W - 1, H - 1]) or [W - 1, H - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obstacles:
                resources.append((x, y))

    def cd(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < W and 0 <= ny < H) or (nx, ny) in obstacles:
            continue

        # If no resources visible, move to improve distance vs opponent (deterministic center-ish pull).
        if not resources:
            val = cd(nx, ny, ox, oy) * 2 + (W - abs(nx - (W - 1) / 2) - 1) * 0
            if val > best_val or (val == best_val and (dx, dy) < best_move):
                best_val, best_move = val, (dx, dy)
            continue

        # Choose resource that maximizes "tempo" advantage (I arrive earlier than opponent).
        cur_best = -10**18
        for rx, ry in resources:
            self_d = cd(nx, ny, rx, ry)
            opp_d = cd(ox, oy, rx, ry)
            # Prefer grabbing nearer resources, and blocking where opponent is closer.
            tempo = opp_d - self_d
            val = tempo * 100 - self_d * 3 + cd(nx, ny, ox, oy) * 0.5
            cur_best = val if val > cur_best else cur_best

        # Small preference for moving closer to the currently "best" resource while keeping away from opponent.
        # Add deterministic tie-break via sum of coordinates.
        val = cur_best + (-(abs(nx - ox) + abs(ny - oy)) * 0.01) - (nx + ny) * 1e-6
        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val, best_move = val, (dx, dy)

    return [int(best_move[0]), int(best_move[1])]