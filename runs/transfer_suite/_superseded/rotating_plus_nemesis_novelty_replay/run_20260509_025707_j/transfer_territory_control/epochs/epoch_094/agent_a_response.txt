def choose_move(observation):
    sx, sy = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = {(p[0], p[1]) for p in (observation.get("obstacles") or [])}
    my_set = {(p[0], p[1]) for p in (observation.get("self_territory") or [])}
    opp_set = {(p[0], p[1]) for p in (observation.get("opponent_territory") or [])}
    un_set = {(p[0], p[1]) for p in (observation.get("unclaimed_cells") or [])}
    if (sx, sy) in obstacles:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def near_opp(x, y):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx or dy:
                    if (x + dx, y + dy) in opp_set:
                        return True
        return False

    def edge_penalty(x, y):
        return min(x, w - 1 - x, y, h - 1 - y)  # larger means more central

    def my_frontier_bias(x, y):
        # prefer connecting to our territory edge (more likely to expand safely)
        c = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx or dy and (x + dx, y + dy) in my_set:
                    c += 1
        return c

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        # Capturing immediate opponent cells (flipping on entry)
        cap = 1 if (nx, ny) in opp_set else 0
        # Otherwise, move into unclaimed that reduces opponent's edge pressure
        is_un = 1 if (nx, ny) in un_set else 0

        # Deterministic scoring: maximize capture, then claim unclaimed, then centrality,
        # and keep some safety by avoiding cells with many obstacles nearby.
        obst = 0
        for ox in (-1, 0, 1):
            for oy in (-1, 0, 1):
                if ox or oy and (nx + ox, ny + oy) in obstacles:
                    obst += 1

        central = edge_penalty(nx, ny)
        frontier = my_frontier_bias(nx, ny)
        score = (cap * 10_000) + (is_un * 2000) + (central * 20) + (frontier * 5) - (obst * 2)

        # If no unclaimed/capture, drift towards central while still respecting frontier
        if best_score is None or score > best_score or (score == best_score and (nx, ny) < best):
            best_score = score
            best = (nx, ny)

    if best is None:
        return [0, 0]
    return [best[0] - sx, best[1] - sy]