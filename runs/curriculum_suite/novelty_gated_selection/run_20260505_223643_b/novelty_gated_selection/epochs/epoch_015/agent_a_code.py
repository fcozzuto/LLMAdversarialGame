def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obstacles_list:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def best_target(px, py):
        if not resources:
            return (px, py)
        best = None
        bestv = None
        for rx, ry in resources:
            d = cheb(px, py, rx, ry)
            if best is None or d < bestv or (d == bestv and (rx+ry) < (best[0]+best[1])):
                best = (rx, ry)
                bestv = d
        return best

    if not resources:
        return [0, 0]

    # Primary: take nearest resource to us.
    tx, ty = best_target(sx, sy)
    # Secondary: estimate opponent's nearest resource and try to slow it down.
    ptx, pty = best_target(ox, oy)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = -10**18

    my0 = cheb(sx, sy, tx, ty)
    op0 = cheb(ox, oy, ptx, pty)

    # If we can’t change much, move toward a "disrupt" cell near opponent target.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        myd = cheb(nx, ny, tx, ty)

        # Disruption heuristic: moving closer to the opponent-target reduces their "free" progress.
        # Also penalize moves that allow a shorter path for the opponent by approaching the same line.
        disrupt_cell = (ptx, pty)
        # Opponent improvement proxy: how much closer opponent would be after our move if it also
        # heads greedily (we approximate by comparing our move's effect on distance to disrupt_cell).
        # Use symmetry: prefer moves that keep our next step far from opponent.
        opd = cheb(nx, ny, ptx, pty)

        # If next cell is adjacent to an obstacle or blocks a corridor, slight reward:
        # (deterministic local pattern)
        wall_adj = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                cx, cy = nx + ax, ny + ay
                if (cx, cy) in obstacles:
                    wall_adj += 1

        # Score: prioritize our progress, then slow the opponent indirectly, then avoid clustering on their target.
        val = (-(myd) * 1000) + (opd * 10) + (wall_adj * 3) + (my0 - myd) * 50
        # Tie-break: deterministic toward increasing x,y to avoid oscillations.
        if val > best_val or (val == best_val and (nx, ny) > (sx + best_move[0], sy + best_move[1])):
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]