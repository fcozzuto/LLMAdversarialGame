def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    resources = list(map(tuple, observation.get("resources") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))
    self_terr = set(map(tuple, observation.get("self_territory") or []))
    opp_terr = set(map(tuple, observation.get("opponent_territory") or []))
    scores = observation.get("scores") or {}
    self_name = observation.get("self_name", "agent_a")
    opp_name = observation.get("opponent_name", "agent_b")
    my_score = float(scores.get(self_name, 0.0) or 0.0)
    op_score = float(scores.get(opp_name, 0.0) or 0.0)

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def legal(nx, ny):
        return inb(nx, ny) and (nx, ny) not in obstacles

    def dist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    aggressive = my_score < op_score
    best_move = [0, 0]
    best_key = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        key = 0.0

        if (nx, ny) in unclaimed:
            key += 100.0
        elif (nx, ny) in opp_terr:
            key += 85.0
        elif (nx, ny) in self_terr:
            key += 12.0
        else:
            key += 20.0

        if resources:
            rdx = min(dist(nx, ny, rx, ry) for rx, ry in resources)
            key += max(0.0, 40.0 - rdx * 6.0)

        d_to_opp = dist(nx, ny, ox, oy)
        key += (-2.5 * d_to_opp) if aggressive else (2.0 * d_to_opp)

        if best_key is None or key > best_key:
            best_key = key
            best_move = [dx, dy]
        elif key == best_key:
            if [dx, dy] < best_move:
                best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]