def choose_move(observation):
    turn = observation.get("turn_index", 0)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    me = observation.get("self_position", [0, 0])
    opp = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    # deterministic rotation for variety
    k = turn % len(moves)
    moves = moves[k:] + moves[:k]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        return abs(a[0]-b[0]) + abs(a[1]-b[1])

    def safe(nx, ny):
        return inb(nx, ny) and (nx, ny) not in obstacles

    best_move = [0, 0]
    best_score = -10**9

    # if resources exist, prefer moving towards nearest resource with opponent competition awareness
    if resources:
        for dx, dy in moves:
            nx, ny = me[0] + dx, me[1] + dy
            if not safe(nx, ny):
                continue
            # score based on closeness to nearest resource vs opponent distance
            sc = 0
            for rx, ry in resources:
                d_my = dist((nx, ny), (rx, ry))
                d_opp = dist(opp, (rx, ry))
                sc += (d_opp - d_my)
            # slight bias to reduce distance to opponent when no strong resource pull
            if not resources:
                sc -= dist((nx, ny), opp)
            # discourage stepping onto opponent
            if (nx, ny) == tuple(opp):
                sc -= 1000
            if sc > best_score:
                best_score = sc
                best_move = [dx, dy]
    else:
        # No resources: keep safe while maximizing distance from opponent and avoiding obstacles
        for dx, dy in moves:
            nx, ny = me[0] + dx, me[1] + dy
            if not safe(nx, ny):
                continue
            sc = -dist((nx, ny), opp) * 2
            # avoid being adjacent to obstacles
            for ox, oy in obstacles:
                d = dist((nx, ny), (ox, oy))
                if d == 0:
                    sc -= 1000
                elif d == 1:
                    sc -= 2
            if sc > best_score:
                best_score = sc
                best_move = [dx, dy]

    return best_move