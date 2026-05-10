def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set((int(p[0]), int(p[1])) for p in obstacles_list)

    deltas = [(-1, -1), (0, -1), (1, -1),
              (-1, 0), (0, 0), (1, 0),
              (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx + dy

    def best_val_for(nx, ny):
        if not resources:
            # drift toward opponent's side lightly to deny
            return -man(nx, ny, ox, oy) - (nx + ny) * 0.001
        best = -10**18
        for rx, ry in resources:
            ds = man(nx, ny, rx, ry)
            do = man(ox, oy, rx, ry)
            # race priority; commit when we're at/near the resource
            val = (do - ds) * 2000 - ds - do // 2
            if ds == 0:
                val += 10**9
            elif ds == 1:
                val += 10**6
            elif ds == 2:
                val += 10**4
            # small tie-break toward closer resources to reduce dithering
            val -= ds * 5
            if val > best:
                best = val
        return best

    best_move = [0, 0]
    best_score = -10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        score = best_val_for(nx, ny)
        if (not inb(nx, ny)) or ((nx, ny) in obstacles):
            score -= 10**12
        # prefer moves that reduce our closest-resource distance
        if resources and inb(nx, ny) and (nx, ny) not in obstacles:
            curr_best = min(man(sx, sy, rx, ry) for rx, ry in resources)
            next_best = min(man(nx, ny, rx, ry) for rx, ry in resources)
            score += (curr_best - next_best) * 200
        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]