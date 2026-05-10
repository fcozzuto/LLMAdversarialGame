def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = observation.get("resources") or []
    res_list = []
    for p in resources:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                res_list.append((x, y))

    role = (observation.get("self_role") or "").lower()
    pursue = any(k in role for k in ("pursuer", "hunter", "chaser", "pursuit"))

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    best_dxdy = [0, 0]
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            score = -10**15
        else:
            md_res = 10**9
            for rx, ry in res_list:
                d = abs(nx - rx) + abs(ny - ry)
                if d < md_res:
                    md_res = d
            res_score = 0.0 if not res_list else (50.0 / (md_res + 1.0))
            if pursue:
                opp_score = - (abs(nx - ox) + abs(ny - oy))
            else:
                opp_score = (abs(nx - ox) + abs(ny - oy)) * 0.4
            edge_pen = 0
            if nx == 0 or ny == 0 or nx == w - 1 or ny == h - 1:
                edge_pen = -0.5
            score = res_score + opp_score + edge_pen
        if score > best_score:
            best_score = score
            best_dxdy = [dx, dy]

    return best_dxdy