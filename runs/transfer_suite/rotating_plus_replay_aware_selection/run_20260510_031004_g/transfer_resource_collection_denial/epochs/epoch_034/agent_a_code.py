def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    resources = observation.get("resources") or []
    obstacles_list = observation.get("obstacles") or []
    obs = set()
    for p in obstacles_list:
        if p is None or len(p) < 2:
            continue
        x, y = int(p[0]), int(p[1])
        if 0 <= x < w and 0 <= y < h:
            obs.add((x, y))

    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    dirs = [-1, 0, 1]
    moves = []
    for dx in dirs:
        for dy in dirs:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                moves.append((dx, dy))
    if not moves:
        moves = [(0, 0)]

    best_move = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        move_score = None
        for i in range(len(resources)):
            rx, ry = int(resources[i][0]), int(resources[i][1])
            sd0 = cheb(sx, sy, rx, ry)
            od = cheb(ox, oy, rx, ry)
            sd1 = cheb(nx, ny, rx, ry)
            gain = od - sd1  # higher means we are closer than opponent after this move
            # Encourage reducing distance and picking higher "win pressure" targets
            score = (gain, -sd1, -sd0, -i)
            if (move_score is None) or (score > move_score):
                move_score = score
        if (best_score is None) or (move_score > best_score):
            best_score = move_score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]