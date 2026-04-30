def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])
    ox, oy = int(observation["opponent_position"][0]), int(observation["opponent_position"][1])
    resources = [(int(p[0]), int(p[1])) for p in (observation.get("resources") or [])]
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []))
    if not resources:
        return [0, 0]
    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    INF = 10**9

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def valid(x, y): return inb(x, y) and (x, y) not in obstacles

    def bfs(x0, y0):
        dist = [[INF] * h for _ in range(w)]
        if not valid(x0, y0):
            return dist
        dist[x0][y0] = 0
        qx = [x0]; qy = [y0]; qi = 0
        while qi < len(qx):
            x = qx[qi]; y = qy[qi]; qi += 1
            nd = dist[x][y] + 1
            for dx, dy in moves:
                nx, ny = x + dx, y + dy
                if valid(nx, ny) and nd < dist[nx][ny]:
                    dist[nx][ny] = nd
                    qx.append(nx); qy.append(ny)
        return dist

    distS = bfs(sx, sy)
    distO = bfs(ox, oy)

    best = None
    best_val = -10**18
    for rx, ry in resources:
        ds = distS[rx][ry]; do = distO[rx][ry]
        if ds >= INF:
            continue
        # Materially different from "pure race": strongly prefer targets we are likely to secure,
        # but also keep a push for later wins by valuing (do-ds) more than raw ds.
        val = (do - ds) * 10 - ds
        # If opponent is already very close, down-rank heavily to avoid dead races.
        if do <= ds:
            val -= 50
        # If resource is very far for us, avoid.
        if ds > 10:
            val -= (ds - 10) * 2
        if val > best_val:
            best_val = val
            best = (rx, ry)

    tx, ty = best if best is not None else resources[0]
    cx, cy = sx, sy
    # Greedy step toward target with safety: don't enter squares that make opponent closer advantage.
    best_step = (0, 0)
    best_step_val = -10**18
    for dx, dy in moves:
        nx, ny = cx + dx, cy + dy
        if not valid(nx, ny):
            continue
        ns = distS[nx][ny]
        nds = distS[tx][ty]
        # If target unreachable from that step, penalize.
        if ns >= INF or nds >= INF:
            step_val = -10**18
        else:
            # Prefer reducing our distance to target and preventing opponent from overtaking.
            my_to_target = abs(nx - tx) + abs(ny - ty)
            opp_adv = distO[nx][ny] - distS[nx][ny]
            step_val = -my_to_target * 2 + (opp_adv) * 3 - abs((ox - nx)) * 0.01 - abs((oy - ny)) * 0.01
            # If moving would put opponent strictly closer to target than we are (race avoidance), penalize.
            if distO[tx][ty] <= distS[tx][ty] and dx == 0 and dy == 0:
                step_val -= 20
        if step_val > best_step_val:
            best_step_val = step_val
            best_step = (dx, dy)

    return [int(best_step[0]), int(best_step[1])]