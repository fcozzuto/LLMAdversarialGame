def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set((x, y) for x, y in observation.get("obstacles", []))
    dxs = (-1, 0, 1)
    moves = [(dx, dy) for dx in dxs for dy in dxs]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        return abs(a[0]-b[0]) + abs(a[1]-b[1])

    def best_target():
        if not resources:
            return (sx, sy)
        best = None
        best_val = -10**9
        for r in resources:
            d1 = dist((sx, sy), r)
            d2 = dist((ox, oy), r)
            # Prefer contested resources where we are closer; break ties by nearer overall.
            val = (d2 - d1) * 5 - d1
            if val > best_val:
                best_val = val
                best = r
        return best

    def greedy_next(px, py, target):
        # 1-step greedy: minimize distance to target, avoid obstacles if possible.
        best = (px, py)
        bd = 10**9
        for dx, dy in moves:
            nx, ny = px + dx, py + dy
            if not inside(nx, ny):
                continue
            if (nx, ny) in obstacles:
                continue
            d = dist((nx, ny), target)
            if d < bd:
                bd = d
                best = (nx, ny)
        return best

    target = best_target()
    my_next_opp = greedy_next(ox, oy, target)

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        # If move into obstacle, it would be rejected; still allow evaluation but penalize strongly.
        hit = (nx, ny) in obstacles
        if hit:
            score = -10**12
        else:
            my_d = dist((nx, ny), target)
            opp_d = dist(my_next_opp, target)
            sep = dist((nx, ny), my_next_opp)
            # Promote reaching target sooner than opponent and increasing separation.
            score = (-my_d * 6) + ((opp_d - my_d) * 8) + (sep * 1.5)
            # Small bias toward collecting when at resource cell.
            if (nx, ny) in resources:
                score += 1000
            # Discourage moving adjacent to opponent when contesting.
            if dist((nx, ny), my_next_opp) <= 2:
                score -= 15
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]