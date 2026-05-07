def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def d(a, b, c, e):
        return max(abs(c - a), abs(e - b))  # Chebyshev

    def best_target_from(posx, posy):
        best = None
        bestk = None
        for rx, ry in resources:
            myd = d(sx, sy, rx, ry)
            oppd = d(ox, oy, rx, ry)
            # prefer resources we can potentially win: smaller (myd-oppd), then nearer to opponent-block advantage
            key = (myd - oppd, myd, -oppd, rx, ry)
            if bestk is None or key < bestk:
                bestk = key
                best = (rx, ry)
        return best

    if not resources:
        tx, ty = w // 2, h // 2
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        nx, ny = sx + dx, sy + dy
        return [dx, dy] if valid(nx, ny) else [0, 0]

    tx, ty = best_target_from(sx, sy)

    best_move = [0, 0]
    best_score = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        # Strongly prefer stepping onto a resource immediately.
        immediate = 1 if (nx, ny) in set(tuple(r) for r in resources) else 0

        # Evaluate contest over the best local target after this move.
        local_best = None
        localk = None
        for rx, ry in resources:
            myd = d(nx, ny, rx, ry)
            oppd = d(ox, oy, rx, ry)
            # maximize advantage = oppd - myd; tie-break closer to resource; and avoid giving opponent an immediate edge
            key = (-(oppd - myd), myd, oppd, rx, ry)
            if localk is None or key < localk:
                localk = key
                local_best = (rx, ry)

        rx, ry = local_best
        myd = d(nx, ny, rx, ry)
        oppd = d(ox, oy, rx, ry)
        advantage = oppd - myd

        # small bias toward moving toward initial chosen target
        to_init = -d(nx, ny, tx, ty)

        # if opponent could move to the same square next turn easily, penalize moves that worsen our race
        opp_can_reach_now = 1 if d(ox, oy, nx, ny) <= 1 else 0
        score = immediate * 10**6 + advantage * 1000 + to_init * 3 - opp_can_reach_now * 5 + (0 if (nx, ny) == (tx, ty) else -1)

        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move