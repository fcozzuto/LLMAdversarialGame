def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    role_s = str(observation.get("self_role", "")).lower()
    i_am_evader = not any(k in role_s for k in ("pursuer", "chaser", "catch", "pursuit"))

    obstacles = observation.get("obstacles") or []
    blocked = set()
    for p in obstacles:
        if p and len(p) >= 2:
            bx, by = int(p[0]), int(p[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocked

    def dist_cheb(x, y):
        dx = abs(x - ox)
        dy = abs(y - oy)
        return dx if dx >= dy else dy

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    far_corner = max(corners, key=lambda c: dist_cheb(c[0], c[1]))

    # Prefer higher indices in list for deterministic tie-breaking (order matters)
    candidates = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best_move = (0, 0)
    best_val = None
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        d = dist_cheb(nx, ny)
        if (nx, ny) == (ox, oy):
            # No capture radius given (0); this move is still meaningful for pursuer
            pass

        # Wall/obstacle awareness: penalize moving adjacent to obstacles (evader) or stepping toward them (pursuer)
        adj_obs = 0
        for ax, ay in candidates:
            tx, ty = nx + ax, ny + ay
            if 0 <= tx < w and 0 <= ty < h and (tx, ty) in blocked:
                adj_obs += 1

        if i_am_evader:
            tcx, tcy = far_corner
            corner_prog = dist_cheb(nx, ny) - dist_cheb(sx, sy)
            to_corner = dist_cheb(nx, ny)
            # Flee and steer to far corner; also avoid obstacle clutter (wall_runner style)
            val = d * 10 + corner_prog * 2 + (to_corner == d) * 0 - adj_obs * 3
        else:
            # Pursuer: minimize distance; also avoid getting stuck near obstacles
            tcx, tcy = far_corner  # irrelevant but keeps structure simple/deterministic
            val = -d * 10 + (dist_cheb(sx, sy) - d) * 2 - adj_obs * 1

        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]