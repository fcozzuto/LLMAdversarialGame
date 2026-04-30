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

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    nearest_res = None
    if resources:
        nearest_res = min(resources, key=lambda r: dist((sx, sy), r))

    # Avoid immediate capture by opponent: if opponent is adjacent, move away if possible
    opp_adjacent = max(abs(ox - sx), abs(oy - sy)) <= 1

    # choose move to approach nearest resource, but prefer moves that increase distance from opponent if near
    best = None
    best_score = None
    for dx, dy, nx, ny in legal:
        score = 0
        if nearest_res is not None:
            score -= dist((nx, ny), nearest_res) * 2  # approach resource
        if opp_adjacent:
            score += dist((nx, ny), (ox, oy))  # increase distance from opponent
        # small bias to stay near center
        score += -abs(nx - w//2) - abs(ny - h//2)
        if best is None or score > best_score:
            best = (dx, dy, nx, ny)
            best_score = score

    if best is None:
        return [0, 0]
    return [best[0], best[1]]