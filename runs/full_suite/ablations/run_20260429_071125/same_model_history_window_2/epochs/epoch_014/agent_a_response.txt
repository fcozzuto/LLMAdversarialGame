def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obs_list:
        if p is not None and len(p) == 2:
            obstacles.add((p[0], p[1]))

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2; dx = -dx if dx < 0 else dx
        dy = y1 - y2; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy

    def tie_key(r):
        x, y = r
        return (x, y)

    # If no resources, push toward opponent position (deterministic)
    if not resources:
        best_score = -10**9
        best_move = [0, 0]
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny):
                continue
            d = cheb(nx, ny, ox, oy)
            edge = (nx == 0) + (nx == w - 1) + (ny == 0) + (ny == h - 1)
            score = -d - 0.02 * edge
            if score > best_score or (score == best_score and (dx, dy) < (best_move[0], best_move[1])):
                best_score = score; best_move = [dx, dy]
        return best_move

    resources_sorted = sorted(resources, key=tie_key)
    best_score = -10**18
    best_move = [0, 0]

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        # Prefer moves that become relatively closer than opponent to some resource
        best_r_score = -10**18
        for r in resources_sorted:
            rx, ry = r
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            # If opponent is closer, still allow if we catch up; reward relative advantage
            r_score = (od - sd) - 0.03 * sd + 0.01 * (od - sd == 0)
            if r_score > best_r_score:
                best_r_score = r_score
        edge = (nx == 0) + (nx == w - 1) + (ny == 0) + (ny == h - 1)
        # Mild obstacle-nearby avoidance: penalize moves that go into cells with many blocked neighbors
        block_neigh = 0
        for ax, ay in deltas:
            x2, y2 = nx + ax, ny + ay
            if not (0 <= x2 < w and 0 <= y2 < h) or (x2, y2) in obstacles:
                block_neigh += 1
        score = best_r_score - 0.01 * edge - 0.002 * block_neigh
        if score > best_score or (score == best_score and (dx, dy) < (best_move[0], best_move[1])):
            best_score = score
            best_move = [dx, dy]

    return best_move