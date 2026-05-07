def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    ox, oy = observation.get("opponent_position") or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        x, y = int(p[0]), int(p[1])
        if 0 <= x < w and 0 <= y < h:
            obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        x, y = int(r[0]), int(r[1])
        if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
            resources.append((x, y))
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def adj_obstacle(x, y):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in obstacles:
                    return True
        return False

    # Strategic shift: prioritize resources where we are likely to beat the opponent NEXT step,
    # but break ties by choosing the one that also pulls us away from immediate obstacle-adjacency.
    best_move = (0, 0)
    best_val = -10**30
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        self_next_d_opp = cheb(nx, ny, ox, oy)
        penalty = (1 if adj_obstacle(nx, ny) else 0)
        # Encourage keeping distance from opponent while targeting winnable resources (denial).
        val = -2 * self_next_d_opp - 3 * penalty

        for rx, ry in resources:
            self_d = cheb(nx, ny, rx, ry)
            opp_d = cheb(ox, oy, rx, ry)
            # Winnable if self_d <= opp_d; stronger if we are strictly closer.
            win_margin = opp_d - self_d
            if win_margin >= 0:
                val += 20 * win_margin
                val -= self_d  # shorter route among winnable targets
            else:
                # If opponent is closer, avoid giving them an easy deny target; still allow
                # movement that blocks by increasing their closeness slightly.
                val += 2 * win_margin

        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]