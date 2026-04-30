def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_val = 10**18

    # Heuristic target selection: take resource where (we are closer than opponent) and also likely earlier.
    # Also penalize moving near obstacles.
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue

        # Obstacle proximity penalty
        pen = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                if (nx + ax, ny + ay) in obstacles:
                    pen += 1 if ax == 0 or ay == 0 else 2

        # Evaluate move by best resource from the new position
        move_val = 10**18
        if resources:
            for rx, ry in resources:
                d_our = cheb(nx, ny, rx, ry)
                d_opp = cheb(ox, oy, rx, ry)
                # Prefer resources where we are closer; if behind, still pick those that minimize lateness.
                rel = d_our - d_opp
                # Encourage immediate capture (lower our distance), but discourage giving opponent better access.
                val = d_our * 10 + (rel * 6) + (d_opp * 2) + (pen * 3)
                # Deterministic preference ordering
                val += (rx + 31 * ry) * 0.0001
                if val < move_val:
                    move_val = val
        else:
            # No visible resources: head toward opponent corner as a proxy to contest future spawns
            target_corner = (w - 1, h - 1)
            move_val = cheb(nx, ny, target_corner[0], target_corner[1]) + pen * 3

        # Tie-break deterministically by preferring non-still if equal
        move_val += (0 if (dx != 0 or dy != 0) else 0.001)

        if move_val < best_val:
            best_val = move_val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]