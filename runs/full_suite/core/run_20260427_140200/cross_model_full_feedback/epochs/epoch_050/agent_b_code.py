def choose_move(observation):
    turn = int(observation.get("turn_index", 0))
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    me = observation.get("self_position", [0, 0])
    opp = observation.get("opponent_position", [0, 0])
    sx, sy = int(me[0]), int(me[1])
    ox, oy = int(opp[0]), int(opp[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def dist(a, b):
        return abs(a[0]-b[0]) + abs(a[1]-b[1])

    if not resources:
        resources = [(sx, sy)]

    dirs = [(-1,-1), (0,-1), (1,-1),
            (-1,0),  (0,0),  (1,0),
            (-1,1),  (0,1),  (1,1)]

    best = None
    best_score = -10**9

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue

        # proximity to nearest resource, and relative position to opponent
        nd = None
        for r in resources:
            d = dist((nx, ny), r)
            if nd is None or d < nd:
                nd = d
        if nd is None:
            nd = 0

        # prefer to approach resource while staying away from opponent
        od = dist((nx, ny), (ox, oy))
        score = -nd*2 - od

        if best is None or score > best_score:
            best_score = score
            best = (nx, ny)

    if best is None:
        return [0, 0]

    tx, ty = best
    dx = tx - sx
    dy = ty - sy
    # clamp to -1,0,1 (though moves here are already within due to grid)
    if dx > 1: dx = 1
    if dx < -1: dx = -1
    if dy > 1: dy = 1
    if dy < -1: dy = -1
    return [dx, dy]