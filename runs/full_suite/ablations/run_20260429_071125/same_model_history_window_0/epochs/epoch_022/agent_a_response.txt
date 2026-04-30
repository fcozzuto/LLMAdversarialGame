def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    obstacles = set((x, y) for x, y in observation.get("obstacles", []))
    resources = observation.get("resources", [])
    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    def dist(a, b, c, d):
        dx = abs(a-c); dy = abs(b-d)
        return dx if dx > dy else dy
    best = None; best_key = None
    for rx, ry in resources:
        ds = dist(sx, sy, rx, ry)
        do = dist(ox, oy, rx, ry)
        adv = do - ds
        key = (adv, -ds, -abs(rx - sx) - abs(ry - sy), rx, ry)
        if best_key is None or key > best_key:
            best_key = key; best = (rx, ry)
    if best is None:
        return [0, 0]
    tx, ty = best
    # Strategic nudge: if opponent is closer (likely contest), bias moving to keep distance from them.
    opp_closer = dist(ox, oy, tx, ty) < dist(sx, sy, tx, ty)
    best_move = (0, 0); best_score = None
    for dx, dy in deltas:
        nx = sx + dx; ny = sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h: 
            continue
        if (nx, ny) in obstacles:
            continue
        d_to = dist(nx, ny, tx, ty)
        # Encourage progress; discourage proximity to opponent if contesting.
        d_op = dist(nx, ny, ox, oy)
        score = (-d_to, d_op if opp_closer else -d_op/2, -(abs(dx)+abs(dy)), dx, dy)
        if best_score is None or score > best_score:
            best_score = score; best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]