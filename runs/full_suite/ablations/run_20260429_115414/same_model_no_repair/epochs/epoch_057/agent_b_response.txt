def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", [])
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []))
    if not resources:
        return [0, 0]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def manh(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def adj_obs(x, y):
        c = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in obstacles:
                    c += 1
        return c

    def clamp(v, a, b):
        return a if v < a else b if v > b else v

    best_mv = (0, 0)
    best_val = -10**18

    cur_to_res = sorted((manh(sx, sy, rx, ry), rx, ry) for rx, ry in resources)
    # Prefer closer resources; also bias toward resources that are not closer to opponent than we are.
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        my_near = 10**9
        opp_near = 10**9
        pick_gain = -10**18
        for rx, ry in resources:
            sd = manh(nx, ny, rx, ry)
            od = manh(ox, oy, rx, ry)
            if sd < my_near:
                my_near = sd
            if od < opp_near:
                opp_near = od
            # reward taking within reach and improving relative advantage
            adv = od - sd
            gain = (1000000 if sd == 0 else 0) + 2000 * adv - 6 * sd
            # discourage targeting far resources when a nearer exists
            if sd > cur_to_res[0][0] + 2:
                gain -= 80
            if gain > pick_gain:
                pick_gain = gain

        # Safety: avoid corners/obstacle adjacency; also avoid stepping adjacent to opponent if it would reduce our advantage
        safety = -20 * adj_obs(nx, ny)
        opp_adj = 1 if max(abs(nx - ox), abs(ny - oy)) == 1 else 0
        # If opponent is very close, staying nearer to the "best relative resource" matters more than chasing distance
        pressure = -120 * opp_adj * clamp((opp_near - my_near), -4, 12) / 8

        # Mild inertia toward not moving away from our best resource
        inertia = -3 * my_near + 2 * (opp_near - my_near)

        # Total
        val = pick_gain + safety + pressure + inertia

        if val > best_val:
            best_val = val
            best_mv = (dx, dy)

    return [int(best_mv[0]), int(best_mv[1])]