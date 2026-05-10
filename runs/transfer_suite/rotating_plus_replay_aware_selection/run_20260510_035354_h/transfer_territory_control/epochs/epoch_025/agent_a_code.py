def choose_move(observation):
    ax, ay = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = observation.get("obstacles") or []
    unclaimed = observation.get("unclaimed_cells") or []
    my_t = observation.get("self_territory") or []
    op_t = observation.get("opponent_territory") or []

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    obs_set = {(x, y) for x, y in obstacles if inb(x, y)}
    my_set = {(x, y) for x, y in my_t if inb(x, y)}
    op_set = {(x, y) for x, y in op_t if inb(x, y)}
    un_set = {(x, y) for x, y in unclaimed if inb(x, y)}

    # Quick access: nearest unclaimed distance (exact, but over set; bounded by input size)
    un_list = list(un_set)
    op_list = list(op_set)

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def mindist(points, x, y):
        if not points: return 999
        best = 999
        for px, py in points:
            d = abs(px - x) + abs(py - y)
            if d < best: best = d
        return best

    def adj_has_set(x, y, s):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0: 
                    continue
                nx, ny = x + dx, y + dy
                if (nx, ny) in s:
                    return True
        return False

    best_move = [0, 0]
    best_score = -10**9
    nearest_un = mindist(un_list, ax, ay)

    for dx, dy in deltas:
        nx, ny = ax + dx, ay + dy
        if not inb(nx, ny) or (nx, ny) in obs_set:
            continue

        base = 0
        if (nx, ny) in op_set: base += 60
        elif (nx, ny) in un_set: base += 45
        elif (nx, ny) in my_set: base += 12
        else: base += 0

        if adj_has_set(nx, ny, op_set): base += 18
        if any((nx + ox, ny + oy) in obs_set for ox in (-1, 0, 1) for oy in (-1, 0, 1) if (ox, oy) != (0, 0)): base -= 6

        d_un = mindist(un_list, nx, ny)
        d_op = mindist(op_list, nx, ny)

        # Tie-breakers: closer to unclaimed, also slightly closer to opponent to pressure sweeps
        score = base * 1000 - d_un * 10 - d_op
        if (un_list and nearest_un != 999) and (d_un < nearest_un):
            score += 30

        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move