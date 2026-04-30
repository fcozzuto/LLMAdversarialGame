def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    gw = observation.get("grid_width", 8)
    gh = observation.get("grid_height", 8)

    obs = set((x, y) for x, y in obstacles)

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def diag_dist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def cell_blocked(nx, ny):
        if not inb(nx, ny):
            return True
        return (nx, ny) in obs

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    if not resources:
        dx = -1 if sx > ox else (1 if sx < ox else 0)
        dy = -1 if sy > oy else (1 if sy < oy else 0)
        return [dx, dy]

    cx = (gw - 1) / 2.0
    cy = (gh - 1) / 2.0

    best_move = (0, 0)
    best_val = -10**18

    # Choose move by looking one step ahead and picking the best target with an opponent-advantage heuristic.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if cell_blocked(nx, ny):
            val = -10**12
        else:
            cur_best = -10**18
            for rx, ry in resources:
                if not inb(rx, ry) or (rx, ry) in obs:
                    continue
                ds = diag_dist(nx, ny, rx, ry)
                do = diag_dist(ox, oy, rx, ry)
                # Lead over opponent dominates; add small penalties/bonuses for stability and centrality.
                lead = do - ds
                center = -0.001 * ((rx - cx) * (rx - cx) + (ry - cy) * (ry - cy))
                score = lead * 1200 - ds * 3 + center
                if score > cur_best:
                    cur_best = score
            val = cur_best
            # Encourage reducing distance to the currently most threatening resource even if equal scores.
            if val == cur_best:
                pass
        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]