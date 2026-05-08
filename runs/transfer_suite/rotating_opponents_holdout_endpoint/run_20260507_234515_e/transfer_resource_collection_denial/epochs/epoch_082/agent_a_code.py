def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    ox, oy = observation.get("opponent_position", (w - 1, h - 1))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(a, b, c, d):
        dx = a - c
        if dx < 0:
            dx = -dx
        dy = b - d
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    opp_target = min(resources, key=lambda t: (dist(ox, oy, t[0], t[1]), t[0], t[1]))

    neigh = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    best_val = -10**18

    for dx, dy in neigh:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        landing_resource = (nx, ny) in resources
        # Choose our target as the closest resource from the prospective move
        my_target = min(resources, key=lambda t: (dist(nx, ny, t[0], t[1]), t[0], t[1]))
        my_d = dist(nx, ny, my_target[0], my_target[1])
        opp_d = dist(ox, oy, my_target[0], my_target[1])

        # Defensive term: increase value if we move away from opponent's likely target
        defend_d = dist(nx, ny, opp_target[0], opp_target[1])
        opp_def = dist(ox, oy, opp_target[0], opp_target[1])

        val = 0
        val += (1000 if landing_resource else 0)
        val += -10 * my_d
        val += 4 * opp_d  # prefer positions where opponent is farther from our target
        val += 1.5 * (defend_d - opp_def)  # slight push to avoid giving easy access

        # Tie-break deterministically toward smallest dx, then dy
        if val > best_val or (val == best_val and (dx, dy) < (best_move[0], best_move[1])):
            best_val = val
            best_move = [dx, dy]

    return best_move