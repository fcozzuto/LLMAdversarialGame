def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    role = (observation.get("self_role") or "").lower()
    is_evader = ("evader" in role) or ("runner" in role) or ("escape" in role) or ("fugitive" in role)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    far_corner = max(corners, key=lambda c: (man(c[0], c[1], ox, oy), c[0] - 3 * c[1] - c[0]))
    cx, cy = far_corner

    best = None
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d_opp = man(nx, ny, ox, oy)

        if is_evader:
            # Prefer increasing distance; if tied, bias toward far_corner while not moving into tighter positions.
            score = (d_opp * 100) + (man(nx, ny, cx, cy) * 2)
            # Mild "escape pressure": avoid squares that reduce distance to opponent next turn most.
            # Deterministic one-ply: estimate best opponent reply distance
            opp_best_next = -10**18
            for odx, ody in moves:
                tx, ty = ox + odx, oy + ody
                if not (0 <= tx < w and 0 <= ty < h) or (tx, ty) in obstacles:
                    continue
                opp_best_next = max(opp_best_next, man(tx, ty, nx, ny))
            # If opponent can get closer (lower d), penalize
            if opp_best_next != -10**18:
                score -= (man(ox, oy, nx, ny) - opp_best_next) * 5
            # Tie-break deterministically by lexicographic move preference
            score -= (dx * 0.01 + dy * 0.02)
        else:
            # Pursuer: greedily minimize distance to opponent; if tie, move to reduce opponent mobility slightly.
            score = (-d_opp * 100) - (man(nx, ny, sx, sy) * 0.01)
            # Count how many safe moves from our next position (prefer tighter chase corridors)
            safe_next = 0
            for mdx, mdy in moves:
                tx, ty = nx + mdx, ny + mdy
                if valid(tx, ty):
                    safe_next += 1
            score += safe_next * 0.1
            score -= (dx * 0.01 + dy * 0.02)

        if score > best_score:
            best_score = score
            best = [dx, dy]

    return best if best is not None else [0, 0]