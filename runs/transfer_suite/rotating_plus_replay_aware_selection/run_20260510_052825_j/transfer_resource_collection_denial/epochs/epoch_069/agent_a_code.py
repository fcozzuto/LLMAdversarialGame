def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def legal(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = None
    best_key = None

    # Heuristic change: prefer moves that increase "win margin" to the most contested nearby resource.
    # Margin = (our_dist_after - opp_dist) ; negative is good (we become closer).
    # We also break ties by distance we travel toward that contested resource.
    for dxm, dym in moves:
        nx, ny = sx + dxm, sy + dym
        if not legal(nx, ny):
            continue

        # Evaluate our best achievable contested resource after this move.
        # Choose the resource that gives smallest (our_dist - opp_dist).
        best_local = None
        for rx, ry in resources:
            if not legal(rx, ry):
                continue
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            margin = sd - od
            # Slight preference for nearer resources once margin is similar.
            # Also ensure deterministic tie-breaking by coordinates.
            key_local = (margin, sd, rx, ry)
            if best_local is None or key_local < best_local:
                best_local = key_local

        if best_local is None:
            continue

        margin, sd, rx, ry = best_local
        # Secondary evaluation: if margin>0 (we're behind), prefer less-bad margin and shorter sd.
        # Primary: minimize margin; when equal, minimize our dist; then deterministic by move.
        key = (margin, sd, rx, ry, dxm, dym)
        if best_key is None or key < best_key:
            best_key = key
            best_move = [dxm, dym]

    if best_move is None:
        return [0, 0]
    return best_move