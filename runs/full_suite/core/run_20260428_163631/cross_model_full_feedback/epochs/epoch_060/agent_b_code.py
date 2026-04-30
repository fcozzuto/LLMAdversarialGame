def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inb(x, y) and (x, y) not in obstacles:
                resources.append((x, y))

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    legal = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    best_move = None
    best_score = -10**18

    for dx, dy, nx, ny in legal:
        # Prefer moving toward closest resource, but avoid getting too close to opponent
        if resources:
            nr = min(md(nx, ny, rx, ry) for rx, ry in resources)
            dist_to_opp = md(nx, ny, ox, oy)
            # Heuristic: get as close as possible to a resource, but keep distance from opponent reasonable
            score = -nr * 1000 - dist_to_opp * 2 + (md(nx, ny, sx, sy) * 0)
        else:
            dist_to_opp = md(nx, ny, ox, oy)
            dist_to_goal_bonus = -dist_to_opp
            score = dist_to_goal_bonus

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    if best_move is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]